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

#name of the directory containing base / the mod folders, e.g. gamedata for Jedi Academy (in lowercase)
DIRNAME = "gamedata"

import os

# returns the prefix and the rest, e.g. ("/foo/bar/JKA/GameData/Base", "textures/img.jpg") (where GameData is DIRNAME)
def SplitPrefix(fullPath):
    normFullPath = os.path.normpath(fullPath)
    searchme = os.path.normcase(normFullPath)
    pos = searchme.find(os.path.sep + DIRNAME + os.path.sep)
    #find /DIRNAME/
    if pos == -1:
        return "", normFullPath
    pos = pos+len(DIRNAME)+2*len(os.path.sep)
    #find first / after that
    pos = searchme.find(os.path.sep, pos)
    if pos == -1:
        return "", normFullPath
    return [normFullPath[:pos+len(os.path.sep)], normFullPath[pos+len(os.path.sep):]]

# removes a file extension, i.e. /foo/bar.baz -> /foo/bar
def RemoveExtension(path):
    return os.path.splitext(path)[0]

# removes leading path, i.e. /foo/bar.baz -> bar.baz
def GetFilename(path):
    return os.path.split(path)[1]

# returns the relative path as used in the game, given the full path and the prefix (as returned by GetPrefix())
def RelPath(fullpath, prefix):
    normPrefix = os.path.normcase(os.path.normcase(prefix))
    normFullpath = os.path.normcase(os.path.normcase(fullpath))
    if normPrefix != os.path.commonprefix([normPrefix, normFullpath]):
        print("Warning: \"", fullpath,"\" does not start with \"",prefix,"\"!", sep="")
        return fullpath
    return os.path.relpath(fullpath, prefix).replace(os.path.sep, "/")

# returns the relative path as used in the game without the extension, given the full path and the prefix (as returned by GetPrefix())
def RelPathNoExt(fullpath, prefix):
    return RemoveExtension(RelPath(fullpath, prefix))

# returns the absolute path of a game path, given its prefix
def AbsPath(relpath, prefix):
    if prefix == "":
        return relpath # would be prefixed "/" otherwise
    return os.path.normpath(os.path.normpath(prefix) + os.path.sep + relpath)

# finds a file given its game name and the possible extensions (usually image extensions).
# Returns (success, filename)
def FindFile(relpath, prefix, extensions):
    absPath = AbsPath(relpath, prefix)
    if os.path.isfile(absPath):
        return True, absPath
    absPath = os.path.splitext(absPath)[0]
    for extension in extensions:
        if os.path.isfile(absPath + "." + extension):
            return True, absPath + "." + extension
    return False, ""

def FileExists(path):
    return os.path.isfile(path)
