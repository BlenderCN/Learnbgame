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

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165

import bpy
import os
from bpy.props import *

#----------------------------------------------------------
#   Settings
#----------------------------------------------------------


def drawDirectories(layout, scn):          
    layout.label("Directories")
    layout.operator("mh.factory_settings")
    layout.operator("mh.save_settings")
    layout.operator("mh.read_settings")
    layout.prop(scn, "MhProgramPath")
    layout.prop(scn, "MhUserPath")
    layout.separator()
    return


def settingsFile(name):
    outdir = os.path.expanduser("~/makehuman/settings/")        
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    return os.path.join(outdir, "make_target.%s" % name)
    

def readDefaultSettings(context):
    fname = settingsFile("settings")
    try:
        fp = open(fname, "rU")
    except:
        print("Did not find %s. Using default settings" % fname)
        return
    
    scn = context.scene    
    for line in fp:
        words = line.split()
        prop = words[0]
        value = words[1].replace("\%20", " ")
        scn[prop] = value
    fp.close()
    return
    

def saveDefaultSettings(context):
    fname = settingsFile("settings")
    fp = open(fname, "w", encoding="utf-8", newline="\n")
    scn = context.scene
    for (key, value) in [
        ("MhProgramPath", scn.MhProgramPath), 
        ("MhUserPath", scn.MhUserPath), 
        ("MhTargetPath", scn.MhTargetPath)]:
        fp.write("%s %s\n" % (key, value.replace(" ", "\%20")))
    fp.close()
    return


def restoreFactorySettings(context):
    scn = context.scene
    scn.MhProgramPath = "/program/makehuman"
    scn.MhUserPath = "~/documents/makehuman"
    scn.MhTargetPath = "/program/makehuman/data/correctives"
    
    
def init():
    bpy.types.Scene.MhProgramPath = StringProperty(
        name = "Program Path",
        default = "/program/makehuman"
    )        
    bpy.types.Scene.MhUserPath = StringProperty(
        name = "User Path",
        default = "~/documents/makehuman"
    )        
    bpy.types.Scene.MhTargetPath = StringProperty(
        name = "Target Path",
        default = "/program/makehuman/data/correctives" 
    )        


