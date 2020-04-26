# Copyright (C) 2018 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
import os

# Blender imports
# NONE!


def makeBashSafe(s:str):
    """ make filenames and paths bash safe """
    # protects against file names that would cause problems with bash calls
    if s.startswith(".") or s.startswith("-"):
        s= "_" + s[1:]
    # protects problematic bash characters with backslash
    chars = "!#$&'()*,;<=>?[]^`{|}~: "
    for char in chars:
        s = s.replace(char, "\\" + char)
    return s


def root_path():
    """ get root system directory """
    return os.path.abspath(os.sep)


def splitpath(path:str):
    """ split path into a list of directories """
    folders = []
    while 1:
        path, folder = os.path.split(path)
        if folder != "":
            folders.append(folder)
        else:
            if path != "": folders.append(path)
            break
    return folders[::-1]
