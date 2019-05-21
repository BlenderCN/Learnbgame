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

# <pep8-80 compliant>

""" This script saves a scene's markers to file."""

import bpy

def save_markers(context, filepath, selected_only):

    # get the active scene and object
    scene = context.scene
    markers = scene.timeline_markers
    framerate = scene.render.fps

    filehandle = open(filepath, 'w')

    for marker in markers:
        if not selected_only or marker.select:
            time = marker.frame / framerate
            filehandle.write("{0:.6f}\t{0:.6f}\t{1}\n".format(time, marker.name))

    # after the whole loop close the file
    filehandle.close()

    return {"FINISHED"}
