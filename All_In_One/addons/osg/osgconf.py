# -*- python-indent: 4; coding: iso-8859-1; mode: python -*-
# Copyright (C) 2008 Cedric Pinson, Jeremy Moles
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#  Cedric Pinson <cedric.pinson@plopbyte.com>
#  Jeremy Moles <jeremy@emperorlinux.com>
import os
import sys
from . import osglog
from . import osgobject

DEBUG = False


def debug(str):
    if DEBUG:
        osglog.log(str)


class Config(object):
    def __init__(self):
        object.__init__(self)
        self.activate()

    def defaultattr(self, attr, value):
        if not hasattr(self, attr):
            setattr(self, attr, value)

    def activate(self):
        self.log_file = None
        self.defaultattr("author", "")
        self.defaultattr("filename", "")

        self.defaultattr("indent", int(2))
        self.defaultattr("float_precision", int(5))
        self.defaultattr("format_num", int(0))
        self.defaultattr("anim_fps", 25.0)
        self.defaultattr("log", True)
        self.defaultattr("selected", "ALL")
        self.defaultattr("relative_path", False)
        self.defaultattr("texture_prefix", "textures")
        self.defaultattr("only_visible", True)
        self.defaultattr("export_anim", True)
        self.defaultattr("object_selected", None)

        self.defaultattr("zero_translations", False)
        self.defaultattr("apply_modifiers", False)
        self.defaultattr("bake_animations", False)
        self.defaultattr("use_quaternions", False)
        self.defaultattr("bake_constraints", True)
        self.defaultattr("bake_frame_step", 1)
        self.defaultattr("arm_rest", False)
        self.defaultattr("osgconv_to_ive", False)
        osgconv_util = "osgconv"
        if sys.platform == 'win32':
            osgconv_util += ".exe"
        self.defaultattr("osgconv_path", osgconv_util)
        self.defaultattr("osgconv_embed_textures", False)
        self.defaultattr("run_viewer", False)
        osgviewer_util = "osgviewer"
        if sys.platform == 'win32':
            osgviewer_util += ".exe"
        self.defaultattr("viewer_path", osgviewer_util)
        self.defaultattr("export_all_scenes", False)
        self.defaultattr("osgconv_cleanup", False)

        self.defaultattr("history", {})
        self.defaultattr("json_materials", False)
        self.defaultattr("json_shaders", False)

        self.filepath = ""
        self.fullpath = ""
        self.exclude_objects = []
        osglog.LOGFILE = None
        status = " without log"
        if self.log:
            status = " with log"
        print("save path %s %s" % (self.fullpath, status))

    def createLogfile(self):
        logfilename = self.getFullName("log")
        osglog.LOGFILE = None
        if self.log:
            self.log_file = open(logfilename, "w", encoding='utf-8')
            osglog.LOGFILE = self.log_file
            # print("log %s %s" % (logfilename, osglog.LOGFILE))
        if self.export_anim is False:
            osglog.log("Animations will not be exported")

    def closeLogfile(self):
        if self.log_file:
            filename = self.log_file.name
            osglog.log("Check log file " + filename)
            self.log_file.close()
            self.log_file = None
            osglog.LOGFILE = None

    def validFilename(self):
        if len(self.filename) == 0:
            return False
        return True

    def initFilePaths(self, filename):
        self.filename = filename
        dirname = os.path.dirname(self.filename)
        if dirname == '':
            dirname = '.'
        basename = os.path.splitext(os.path.basename(self.filename))[0]

        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        self.fullpath = dirname + os.sep
        self.filename = basename
        osgobject.INDENT = self.indent
        osgobject.FLOATPRE = self.float_precision

    def getFilenameIfRelative(self, name):
        if self.relative_path is True:
            return os.path.basename(name)
        return name

    # the directory the file will be written to
    def getFullPath(self):
        return self.fullpath

    def getFullName(self, extension):
        if self.filename[-(len(extension) + 1):] == "." + extension:
            f = "%s%s" % (self.fullpath, self.filename)
        else:
            f = "%s%s.%s" % (self.fullpath, self.filename, extension)
        return f

# FILENAME   = ""
# AUTHOR     = ""
# FLOATPRE   = 5
# FORMATNUM  = 0
# ANIMFPS    = 25.0
# LOGFILE    = None
# LOG        = True
# SELECTED   = "ALL" #"SELECTED_ONLY_WITH_CHILDREN" #False
# BAKE       = ""

# FULLPATH   = ""
