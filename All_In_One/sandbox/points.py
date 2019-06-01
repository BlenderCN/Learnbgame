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
# Script copyright (C) MakeHuman Team 2001-2014
# Coding Standards:    See http://www.makehuman.org/node/165


import os
from struct import pack, unpack
import bpy
from bpy.props import *
from mathutils import Vector

from maketarget.mh import CSettings
_settings = CSettings("hm08")


def getClothModifier(ob):
    for mod in ob.modifiers:
        if mod.type == 'CLOTH':
            return mod
    return None


def readVector(fp):
    bx = fp.read(4)
    if not bx:
        halt
    by = fp.read(4)
    bz = fp.read(4)
    x = unpack("f", bx)[0]
    y = unpack("f", by)[0]
    z = unpack("f", bz)[0]
    return (x,y,z)


def readInt(fp):
    return unpack("i", fp.read(4))[0]


def readBhysFile(folder, name, frame):
    filepath = os.path.join(folder, "%s_%06d_00.bphys" % (name, frame))
    with open(filepath, "rb") as fp:
        fp.read(8)
        nx = readInt(fp)
        nverts = readInt(fp)
        nz = readInt(fp)
        #print("Dimensions %d %d %d" % (nx,nverts,nz))
        locs = []
        for n in range(nverts):
            locs.append( readVector(fp) )
            fp.read(2*12)
        return locs


def writeBhysFile(locs, folder, name, frame):
    filepath = os.path.join(folder, "%s_%06d_00.bphys" % (name, frame))
    with open(filepath, "wb") as fp:
        fp.write(b"B"+b"P"+b"H"+b"Y"+b"S"+b"I"+b"C"+b"S")
        fp.write(pack("i", 2))
        fp.write(pack("i", len(locs)))
        fp.write(pack("i", 22))
        zero = pack("f", 0.0) + pack("f", 0.0) + pack("f", 0.0)
        for loc in locs:
            x,y,z = loc.co
            string = pack("f", x) + pack("f", y) + pack("f", z)
            fp.write(string)
            fp.write(zero)
            fp.write(string)


def printLocs(locs, folder):
    filepath = os.path.join(folder, "locs.txt")
    with open(filepath, "w") as fp:
        for n, loc in enumerate(locs):
            fp.write("%6d %10.4f %10.4f %10.4f\n" % (n, loc[0], loc[1], loc[2]))


def createShape(ob, name):
    if not ob.data.shape_keys:
        skey = ob.shape_key_add(name="Basis", from_mix=False)

    skeys = ob.data.shape_keys.key_blocks
    for skey in skeys:
        if skey.name == name:
            skey.value = 1.0
            return skey

    skey = ob.shape_key_add(name=name, from_mix=False)
    ob.active_shape_key_index = len(skeys)-1
    skey.name = name
    skey.value = 1.0
    return skey


def copyCaches(context, name, folder, mhclo):
    from maketarget.proxy import CProxy
    proxy = CProxy()
    proxy.read(mhclo)
    print(proxy)

    scn = context.scene
    refchar = None
    for ob in scn.objects:
        if ob.name == "RefChar":
            refchar = ob
    if refchar is None:
        raise RuntimeError("No object named \"RefChar\" found.")

    ob = context.object
    skey = createShape(ob, name)
    rkey = createShape(refchar, name)
    offset = _settings.vertices["Hair"][0]

    for frame in range(scn.frame_start, scn.frame_end+1):
        scn.frame_set(frame)
        locs = readBhysFile(os.path.join(folder, "blendcache_fem"), name, frame)
        for n,loc in enumerate(locs):
            rkey.data[n+offset].co = loc
        #writeBhysFile(locs, folder, "x"+name, frame)
        proxy.update(rkey.data, skey.data)
        scn.update()
        print("Render frame %d" % frame)
        scn.render.filepath = os.path.join(folder, "render", "%04d.png" % frame)
        bpy.ops.render.opengl(write_still=True)
        #bpy.ops.render.render(write_still=True)


class VIEW3D_OT_CopyPointCacheButton(bpy.types.Operator):
    bl_idname = "mp.copy_point_cache"
    bl_label = "Copy Point Cache"
    bl_options = {'UNDO'}

    def execute(self, context):
        copyCaches(context,
            "jump",
            "/home/myblends/projects/characters/fem",
            "/home/svn/data/hair/hairtype01/longhair01.mhclo")
        return{'FINISHED'}

