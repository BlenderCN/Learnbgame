# -*- coding: utf-8 -*-
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
# Created by Matti 'Menithal' Lahtinen

import bpy
import os
from shutil import move as movefile
import subprocess


def bake_fbx(baker_path, fbx, images = []):
    bpy.ops.wm.console_toggle()

    if baker_path is None:
        print("Please set the Bake tool path")
        return {"CANCELLED"}

    print(os.path.isfile(baker_path), baker_path)
    if not os.path.isfile(baker_path) and "oven" in baker_path:
        print("Please set and select the baker tool exe")
        return {"CANCELLED"}

    path = os.path.dirname(os.path.realpath(fbx))
    print("Now Baking Files", path, fbx)
    
    subprocess.call([baker_path, "-i" + fbx, "-o" + path, "-tfbx"])

    bpy.ops.wm.console_toggle()

    #Delete Originals

    return {"FINISHED"}
