#!/usr/bin/python3
#
# io_scene_s3d
#
# Copyright (C) 2011 Steven J Thompson
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import struct
import os

class BinaryFile():

    def getFileSystemSlash(self):
        if os.name == "posix":
            ## POSIX, use forward slash
            slash = "/"
        else:
            ## Probably Windows, use backslash
            slash = "\\"
        return slash

    def openFile(self, path, mode):
        ## Get the file name and directory from the path string

        slash = self.getFileSystemSlash()
        directory = path.split(slash)[:-1]
        self.fileName = path.split(slash)[-1].split(".")[0]
        self.directory = slash.join(directory) + slash

        ## Open the file
        try:
            self.f = open(path, mode)
            return True
        except:
            print("File not found")
            return False

    def closeFile(self):
        self.f.close()

    def getFileName(self):
        return self.fileName

    def getDirectory(self):
        return self.directory

    def readFromFile(self, type, number = 0): 
        if type == "str":
            charString = ''
            char = ''
            while(char != '\x00'):
                char = bytes.decode(struct.unpack("c", self.f.read(1))[0])
                if char != '\x00':
                    charString += str(char)
            return charString
        elif type == "c":
            chars = struct.unpack(number * "c", self.f.read(number))
            return ''.join(bytes.decode(c) for c in chars)
        elif type == "B":
            return struct.unpack(number * "B", self.f.read(number))[0]
        elif type == "H":
            return struct.unpack(number * "H", self.f.read(number * 2))
        elif type == "h":
            return struct.unpack(number * "h", self.f.read(number * 2))
        elif type == "L":
            return struct.unpack(number * ">L", self.f.read(number * 4))
        elif type == "f":
            return struct.unpack(number * "f", self.f.read(number * 4))
        elif type == "i":
            return struct.unpack(number * "i", self.f.read(number * 4))

    def writeToFile(self, type, value = 0, endString = True): 
        if type == "s":
            if endString == True:
                value = value + "\x00"
            self.f.write(bytes(value, "UTF-8"))
        elif type == "i":
            self.f.write(struct.pack("i", value))
        elif type == "f":
            self.f.write(struct.pack("f", value))
        elif type == "H":
            self.f.write(struct.pack("H", value))
        elif type == "h":
            self.f.write(struct.pack("h", value))
        elif type == "L":
            self.f.write(struct.pack(">L", value))
        elif type == "B":
            self.f.write(struct.pack("B", value))

    def skipFromFile(self, skipBytes): 
        self.f.seek(f.tell() + skipBytes)
