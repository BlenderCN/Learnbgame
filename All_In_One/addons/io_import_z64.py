bl_info = {
    "name":          "Zelda64 Importer",
    "author":        "SoulofDeity",
    "blender":       (2, 7, 5),
    "location":      "File > Import-Export",
    "description":   "Import Zelda64",
    "warning":       "",
    "wiki_url":      "https://code.google.com/p/sods-blender-plugins/",
    "tracker_url":   "https://code.google.com/p/sods-blender-plugins/",
    "support":       'COMMUNITY',
    "category":      "Import-Export",
    "Anim stuff":    "RodLima http://www.facebook.com/rod.lima.96?ref=tn_tnmn"
}

# os independant code introduced July 2015 - zeffii

import os
import struct
import time

import bpy
import mathutils

from bpy import ops
from bpy.props import *
from bpy_extras.image_utils import load_image
from bpy_extras.io_utils import ExportHelper, ImportHelper
from math import *
from mathutils import *
from struct import pack, unpack_from

from mathutils import Vector, Euler, Matrix


def splitOffset(offset):
    return offset >> 24, offset & 0x00FFFFFF


def translateRotation(rot):
    """ axis, angle """
    return Matrix.Rotation(rot[3], 4, Vector(rot[:3]))


def validOffset(segment, offset):
    seg, offset = splitOffset(offset)
    if seg > 15:
        return False
    if offset >= len(segment[seg]):
        return False
    return True


def pow2(val):
    i = 1
    while i < val:
        i <<= 1
    return int(i)


def powof(val):
    num, i = 1, 0
    while num < val:
        num <<= 1
        i += 1
    return int(i)


def mulVec(v1, v2):
    return Vector([v1.x * v2.x, v1.y * v2.y, v1.z * v2.z])


class Tile:
    def __init__(self):
        self.texFmt, self.texBytes = 0x00, 0
        self.width, self.height = 0, 0
        self.rWidth, self.rHeight = 0, 0
        self.txlSize = 0
        self.lineSize = 0
        self.rect = Vector([0, 0, 0, 0])
        self.scale = Vector([1, 1])
        self.ratio = Vector([1, 1])
        self.clip = Vector([0, 0])
        self.mask = Vector([0, 0])
        self.shift = Vector([0, 0])
        self.tshift = Vector([0, 0])
        self.offset = Vector([0, 0])
        self.data = 0x00000000
        self.palette = 0x00000000

    def create(self, segment):
        if exportTextures:
            try:
                os.mkdir(os.path.join(fpath, "textures"))
            except:
                pass
            w = self.rWidth
            if int(self.clip.x) & 1 != 0 and enableTexMirror:
                w <<= 1
            h = self.rHeight
            if int(self.clip.y) & 1 != 0 and enableTexMirror:
                h <<= 1

            # file = open(fpath + "/textures/%08X.tga" % self.data, 'wb')
            file = open(os.path.join(fpath, "textures", "%08X.tga" % self.data), 'wb')

            if self.texFmt == 0x40 or self.texFmt == 0x48 or self.texFmt == 0x50:
                file.write(pack("<BBBHHBHHHHBB", 0, 1, 1, 0, 256, 24, 0, 0, w, h, 8, 0))
                self.writePalette(file, segment)
            else:
                file.write(pack("<BBBHHBHHHHBB", 0, 0, 2, 0, 0, 0, 0, 0, w, h, 32, 8))
            if int(self.clip.y) & 1 != 0 and enableTexMirror:
                self.writeImageData(file, segment, True)
            else:
                self.writeImageData(file, segment)
            file.close()
        try:
            tex = bpy.data.textures.new(name="tex_%08X" % self.data, type='IMAGE')

            # img = load_image(fpath + "/textures/%08X.tga" % self.data)
            img = load_image(os.path.join(fpath, "textures", "%08X.tga" % self.data))

            if img:
                tex.image = img
                if int(self.clip.x) & 2 != 0 and enableTexClamp:
                    img.use_clamp_x = True
                if int(self.clip.y) & 2 != 0 and enableTexClamp:
                    img.use_clamp_y = True
            mtl = bpy.data.materials.new(name="mtl_%08X" % self.data)
            mtl.use_shadeless = True
            mt = mtl.texture_slots.add()
            mt.texture = tex
            mt.texture_coords = 'UV'
            mt.use_map_color_diffuse = True
            if (img.depth == 32):
                mt.use_map_alpha = True
                tex.use_mipmap = True
                tex.use_interpolation = True
                tex.use_alpha = True
                mtl.use_transparency = True
                mtl.alpha = 0.0
                mtl.game_settings.alpha_blend = 'ALPHA'
            return mtl
        except:
            return None

    def calculateSize(self):
        maxTxl, lineShift = 0, 0
        if self.texFmt == 0x00 or self.texFmt == 0x40:
            maxTxl = 4096
            lineShift = 4
        elif self.texFmt == 0x60 or self.texFmt == 0x80:
            maxTxl = 8192
            lineShift = 4
        elif self.texFmt == 0x08 or self.texFmt == 0x48:
            maxTxl = 2048
            lineShift = 3
        elif self.texFmt == 0x68 or self.texFmt == 0x88:
            maxTxl = 4096
            lineShift = 3
        elif self.texFmt == 0x10 or self.texFmt == 0x70:
            maxTxl = 2048
            lineShift = 2
        elif self.texFmt == 0x50 or self.texFmt == 0x90:
            maxTxl = 2048
            lineShift = 0
        elif self.texFmt == 0x18:
            maxTxl = 1024
            lineShift = 2
        lineWidth = self.lineSize << lineShift
        self.lineSize = lineWidth
        tileWidth = self.rect.z - self.rect.x + 1
        tileHeight = self.rect.w - self.rect.y + 1
        maskWidth = 1 << int(self.mask.x)
        maskHeight = 1 << int(self.mask.y)
        lineHeight = 0
        if lineWidth > 0:
            lineHeight = min(int(maxTxl / lineWidth), tileHeight)
        if self.mask.x > 0 and (maskWidth * maskHeight) <= maxTxl:
            self.width = maskWidth
        elif (tileWidth * tileHeight) <= maxTxl:
            self.width = tileWidth
        else:
            self.width = lineWidth
        if self.mask.y > 0 and (maskWidth * maskHeight) <= maxTxl:
            self.height = maskHeight
        elif (tileWidth * tileHeight) <= maxTxl:
            self.height = tileHeight
        else:
            self.height = lineHeight
        clampWidth, clampHeight = 0, 0
        if self.clip.x == 1:
            clampWidth = tileWidth
        else:
            clampWidth = self.width
        if self.clip.y == 1:
            clampHeight = tileHeight
        else:
            clampHeight = self.height
        if maskWidth > self.width:
            self.mask.x = powof(self.width)
            maskWidth = 1 << int(self.mask.x)
        if maskHeight > self.height:
            self.mask.y = powof(self.height)
            maskHeight = 1 << int(self.mask.y)
        if int(self.clip.x) & 2 != 0:
            self.rWidth = pow2(clampWidth)
        elif int(self.clip.x) & 1 != 0:
            self.rWidth = pow2(maskWidth)
        else:
            self.rWidth = pow2(self.width)
        if int(self.clip.y) & 2 != 0:
            self.rHeight = pow2(clampHeight)
        elif int(self.clip.y) & 1 != 0:
            self.rHeight = pow2(maskHeight)
        else:
            self.rHeight = pow2(self.height)
        self.shift.x, self.shift.y = 1.0, 1.0
        if self.tshift.x > 10:
            self.shift.x = 1 << int(16 - self.tshift.x)
        elif self.tshift.x > 0:
            self.shift.x /= 1 << int(self.tshift.x)
        if self.tshift.y > 10:
            self.shift.y = 1 << int(16 - self.tshift.y)
        elif self.tshift.y > 0:
            self.shift.y /= 1 << int(self.tshift.y)
        self.ratio.x = (self.scale.x * self.shift.x) / self.rWidth
        if not enableToon:
            self.ratio.x /= 32
        if int(self.clip.x) & 1 != 0 and enableTexMirror:
            self.ratio.x /= 2
        self.offset.x = self.rect.x
        self.ratio.y = (self.scale.y * self.shift.y) / self.rHeight
        if not enableToon:
            self.ratio.y /= 32
        if int(self.clip.y) & 1 != 0 and enableTexMirror:
            self.ratio.y /= 2
        self.offset.y = 1.0 + self.rect.y

    def writePalette(self, file, segment):
        if self.texFmt == 0x40:
            palSize = 16
        else:
            palSize = 256
        if not validOffset(segment, self.palette + int(palSize * 2) - 1):
            for i in range(256):
                file.write(pack("L", 0))
            return
        seg, offset = splitOffset(self.palette)
        for i in range(256):
            if i < palSize:
                color = unpack_from(">H", segment[seg], offset + (i << 1))[0]
                r = int(8 * ((color >> 11) & 0x1F))
                g = int(8 * ((color >> 6) & 0x1F))
                b = int(8 * ((color >> 1) & 0x1F))
                file.write(pack("BBB", b, g, r))
            else:
                file.write(pack("BBB", 0, 0, 0))

    def writeImageData(self, file, segment, fy=False, df=False):
        if fy:
            dir = (0, self.rHeight, 1)
        else:
            dir = (self.rHeight - 1, -1, -1)
        if self.texFmt == 0x40 or self.texFmt == 0x60 or self.texFmt == 0x80 or self.texFmt == 0x90:
            bpp = 0.5
        elif self.texFmt == 0x00 or self.texFmt == 0x08 or self.texFmt == 0x10 or self.texFmt == 0x70:
            bpp = 2
        elif self.texFmt == 0x48 or self.texFmt == 0x50 or self.texFmt == 0x68 or self.texFmt == 0x88:
            bpp = 1
        else:
            bpp = 4
        lineSize = self.rWidth * bpp
        if not validOffset(segment, self.data + int(self.rHeight * lineSize) - 1):
            size = self.rWidth * self.rHeight
            if int(self.clip.x) & 1 != 0 and enableTexMirror:
                size *= 2
            if int(self.clip.y) & 1 != 0 and enableTexMirror:
                size *= 2
            for i in range(size):
                if self.texFmt == 0x40 or self.texFmt == 0x48 or self.texFmt == 0x50:
                    file.write(pack("B", 0))
                else:
                    file.write(pack(">L", 0x000000FF))
            return
        seg, offset = splitOffset(self.data)
        for i in range(dir[0], dir[1], dir[2]):
            off = offset + int(i * lineSize)
            line = []
            j = 0
            while j < int(self.rWidth * bpp):
                if bpp < 2:
                    color = unpack_from("B", segment[seg], off + int(floor(j)))[0]
                elif bpp == 2:
                    color = unpack_from(">H", segment[seg], off + j)[0]
                else:
                    color = unpack_from(">L", segment[seg], off + j)[0]
                if self.texFmt == 0x40:
                    if floor(j) == j:
                        a = color >> 4
                    else:
                        a = color & 0x0F
                elif self.texFmt == 0x48 or self.texFmt == 0x50:
                    a = color
                elif self.texFmt == 0x00 or self.texFmt == 0x08 or self.texFmt == 0x10:
                    r = int(8 * ((color >> 11) & 0x1F))
                    g = int(8 * ((color >> 6) & 0x1F))
                    b = int(8 * ((color >> 1) & 0x1F))
                    a = int(255 * (color & 0x01))
                elif self.texFmt == 0x80:
                    if floor(j) == j:
                        r = int(16 * (color >> 4))
                    else:
                        r = int(16 * (color & 0x0F))
                    g = r
                    b = g
                    a = 0xFF
                elif self.texFmt == 0x88:
                    r = color
                    g = r
                    b = g
                    a = 0xFF
                elif self.texFmt == 0x68:
                    r = int(16 * (color >> 4))
                    g = r
                    b = g
                    a = int(16 * (color & 0x0F))
                elif self.texFmt == 0x70:
                    r = color >> 8
                    g = r
                    b = g
                    a = color & 0xFF
                elif self.texFmt == 0x18:
                    r = color >> 24
                    g = (color >> 16) & 0xFF
                    b = (color >> 8) & 0xFF
                    a = color & 0xFF
                else:
                    r = 0
                    g = 0
                    b = 0
                    a = 0xFF
                if self.texFmt == 0x40 or self.texFmt == 0x48 or self.texFmt == 0x50:
                    line.extend([a])
                else:
                    line.extend([(b << 24) | (g << 16) | (r << 8) | a])
                j += bpp
            if self.texFmt == 0x40 or self.texFmt == 0x48 or self.texFmt == 0x50:
                file.write(pack("B" * len(line), *line))
            else:
                file.write(pack(">" + "L" * len(line), *line))
            if int(self.clip.x) & 1 != 0 and enableTexMirror:
                line.reverse()
                if self.texFmt == 0x40 or self.texFmt == 0x48 or self.texFmt == 0x50:
                    file.write(pack("B" * len(line), *line))
                else:
                    file.write(pack(">" + "L" * len(line), *line))
        if int(self.clip.y) & 1 != 0 and (not df) and enableTexMirror:
            if fy:
                self.writeImageData(file, segment, False, True)
            else:
                self.writeImageData(file, segment, True, True)


class Vertex:
    def __init__(self):
        self.pos = Vector([0, 0, 0])
        self.uv = Vector([0, 0])
        self.normal = Vector([0, 0, 0])
        self.color = [0, 0, 0, 0]
        self.limb = None

    def read(self, segment, offset):
        if not validOffset(segment, offset + 16):
            return
        seg, offset = splitOffset(offset)
        self.pos.x = unpack_from(">h", segment[seg], offset)[0]
        self.pos.z = unpack_from(">h", segment[seg], offset + 2)[0]
        self.pos.y = -unpack_from(">h", segment[seg], offset + 4)[0]
        self.pos /= 48  # UDK Scale
        self.uv.x = float(unpack_from(">h", segment[seg], offset + 8)[0])
        self.uv.y = float(unpack_from(">h", segment[seg], offset + 10)[0])
        self.normal.x = 0.00781250 * unpack_from("b", segment[seg], offset + 12)[0]
        self.normal.z = 0.00781250 * unpack_from("b", segment[seg], offset + 13)[0]
        self.normal.y = 0.00781250 * unpack_from("b", segment[seg], offset + 14)[0]
        self.color[0] = min(0.00392157 * segment[seg][offset + 12], 1.0)
        self.color[1] = min(0.00392157 * segment[seg][offset + 13], 1.0)
        self.color[2] = min(0.00392157 * segment[seg][offset + 14], 1.0)


class Mesh:
    def __init__(self):
        self.verts, self.uvs, self.colors, self.faces = [], [], [], []
        self.vgroups = {}

    def create(self, hierarchy, offset):
        if len(self.faces) == 0:
            return
        me = bpy.data.meshes.new("me_%08X" % offset)
        ob = bpy.data.objects.new("ob_%08X" % offset, me)
        bpy.context.scene.objects.link(ob)
        bpy.context.scene.objects.active = ob
        me.vertices.add(len(self.verts))

        for i in range(len(self.verts)):
            me.vertices[i].co = self.verts[i]
        me.tessfaces.add(len(self.faces))
        vcd = me.tessface_vertex_colors.new().data
        for i in range(len(self.faces)):
            me.tessfaces[i].vertices = self.faces[i]
            vcd[i].color1 = self.colors[i * 3 + 2]
            vcd[i].color2 = self.colors[i * 3 + 1]
            vcd[i].color3 = self.colors[i * 3]
        uvd = me.tessface_uv_textures.new().data
        for i in range(len(self.faces)):
            if self.uvs[i * 4 + 3]:
                if not self.uvs[i * 4 + 3].name in me.materials:
                    me.materials.append(self.uvs[i * 4 + 3])
                uvd[i].image = self.uvs[i * 4 + 3].texture_slots[0].texture.image
            uvd[i].uv[0] = self.uvs[i * 4 + 2]
            uvd[i].uv[1] = self.uvs[i * 4 + 1]
            uvd[i].uv[2] = self.uvs[i * 4]
        me.calc_normals()
        me.validate()
        me.update()
        if hierarchy:
            for name, vgroup in self.vgroups.items():
                grp = ob.vertex_groups.new(name)
                for v in vgroup:
                    grp.add([v], 1.0, 'REPLACE')
            ob.parent = hierarchy.armature
            mod = ob.modifiers.new(hierarchy.name, 'ARMATURE')
            mod.object = hierarchy.armature
            mod.use_bone_envelopes = False
            mod.use_vertex_groups = True

        ob.animation_data_create()
        action = bpy.data.actions.new(hierarchy.name)
        ob.animation_data.action = action
        # print("Action", action)


class Limb:
    def __init__(self):
        self.parent, self.child, self.sibling = -1, -1, -1
        self.pos = Vector([0, 0, 0])
        self.near, self.far = 0x00000000, 0x00000000
        self.poseBone = None
        self.poseLocPath, self.poseRotPath = None, None
        self.poseLoc, self.poseRot = Vector([0, 0, 0]), None

    def read(self, segment, offset, actuallimb, BoneCount):
        seg, offset = splitOffset(offset)

        rot_offset = offset & 0xFFFFFF
        rot_offset += (0 * (BoneCount * 6 + 8))

        self.pos.x = unpack_from(">h", segment[seg], offset)[0]
        self.pos.z = unpack_from(">h", segment[seg], offset + 2)[0]
        self.pos.y = -unpack_from(">h", segment[seg], offset + 4)[0]
        self.pos /= 48  # UDK Scale
        self.child = unpack_from("b", segment[seg], offset + 6)[0]
        self.sibling = unpack_from("b", segment[seg], offset + 7)[0]
        self.near = unpack_from(">L", segment[seg], offset + 8)[0]
        self.far = unpack_from(">L", segment[seg], offset + 12)[0]

        self.poseLoc.x = unpack_from(">h", segment[seg], rot_offset)[0]
        self.poseLoc.z = unpack_from(">h", segment[seg], rot_offset + 2)[0]
        self.poseLoc.y = unpack_from(">h", segment[seg], rot_offset + 4)[0]
        # print("     Limb ", actuallimb, ":", self.poseLoc.x, ",", self.poseLoc.z, ",", self.poseLoc.y)


class Hierarchy:
    def __init__(self):
        self.name, self.offset = "", 0x00000000
        self.limbCount, self.dlistCount = 0x00, 0x00
        self.limb = []
        self.armature = None

    def read(self, segment, offset):
        if not validOffset(segment, offset + 9):
            return
        self.name = "sk_%08X" % offset
        self.offset = offset
        seg, offset = splitOffset(offset)
        limbIndex_offset = unpack_from(">L", segment[seg], offset)[0]
        if not validOffset(segment, limbIndex_offset):
            print("      ERROR:  Limb index table 0x%08X out of range" % limbIndex_offset)
            return
        limbIndex_seg, limbIndex_offset = splitOffset(limbIndex_offset)
        self.limbCount = segment[seg][offset + 4]
        self.dlistCount = segment[seg][offset + 8]
        for i in range(self.limbCount):
            limb_offset = unpack_from(">L", segment[limbIndex_seg], limbIndex_offset + 4 * i)[0]
            limb = Limb()
            limb.index = i
            self.limb.extend([limb])
            if validOffset(segment, limb_offset + 12):
                limb.read(segment, limb_offset, i, self.limbCount)
            else:
                print("      ERROR:  Limb 0x%02X offset 0x%08X out of range" % (i, limb_offset))[0]
        self.limb[0].pos = Vector([0, 0, 0])
        self.initLimbs(0x00)

    def create(self):
        rx, ry, rz = 90, 0, 0
        if (bpy.context.active_object):
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        for i in bpy.context.selected_objects:
            i.select = False
        self.armature = bpy.data.objects.new(self.name, bpy.data.armatures.new("armature"))
        self.armature.show_x_ray = True
        self.armature.data.draw_type = 'STICK'
        bpy.context.scene.objects.link(self.armature)
        bpy.context.scene.objects.active = self.armature
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        for i in range(self.limbCount):
            bone = self.armature.data.edit_bones.new("limb_%02i" % i)
            bone.use_deform = True
            bone.head = self.limb[i].pos

        for i in range(self.limbCount):
            bone = self.armature.data.edit_bones["limb_%02i" % i]
            if (self.limb[i].parent != -1):
                bone.parent = self.armature.data.edit_bones["limb_%02i" % self.limb[i].parent]
                bone.use_connect = False
            bone.tail = bone.head + Vector([0, 0, 0.0001])
        bpy.ops.object.mode_set(mode='OBJECT')

    def initLimbs(self, i):
        if (self.limb[i].child > -1 and self.limb[i].child != i):
            self.limb[self.limb[i].child].parent = i
            self.limb[self.limb[i].child].pos += self.limb[i].pos
            self.initLimbs(self.limb[i].child)
        if (self.limb[i].sibling > -1 and self.limb[i].sibling != i):
            self.limb[self.limb[i].sibling].parent = self.limb[i].parent
            self.limb[self.limb[i].sibling].pos += self.limb[self.limb[i].parent].pos
            self.initLimbs(self.limb[i].sibling)

    def getMatrixLimb(self, offset):
        j = 0
        index = (offset & 0x00FFFFFF) / 0x40
        for i in range(self.limbCount):
            if self.limb[i].near != 0:
                if (j == index):
                    return self.limb[i]
                j += 1
        return self.limb[0]


class F3DZEX:
    def __init__(self):
        self.segment, self.vbuf, self.tile = [], [], []

        self.animTotal = 0
        self.TimeLine = 0
        self.TimeLinePosition = 0

        for i in range(16):
            self.segment.extend([[]])
            self.vbuf.extend([Vertex()])
        for i in range(2):
            self.tile.extend([Tile()])
            self.vbuf.extend([Vertex()])
        for i in range(14 + 32):
            self.vbuf.extend([Vertex()])
        self.curTile = 0
        self.material = []
        self.hierarchy = []
        self.resetCombiner()

    def setSegment(self, seg, path):
        try:
            file = open(path, 'rb')
            self.segment[seg] = file.read()
            file.close()
        except:
            pass

    def locateHierarchies(self):
        data = self.segment[0x06]
        for i in range(0, len(data), 4):
            if data[i] == 0x06 and (data[i + 3] & 3) == 0 and data[i + 4] != 0:
                offset = unpack_from(">L", data, i)[0] & 0x00FFFFFF
                if offset < len(data):
                    offset_end = offset + (data[i + 4] << 2)
                    if offset_end < len(data):
                        j = offset
                        while j < offset_end:
                            if data[j] != 0x06 or (data[j + 3] & 3) != 0 or (unpack_from(">L", data, j)[0] & 0x00FFFFFF) > len(data):
                                break
                            j += 4
                        if (j == i):
                            j |= 0x06000000
                            print("   hierarchy found at 0x%08X" % j)
                            h = Hierarchy()
                            h.read(self.segment, j)
                            self.hierarchy.extend([h])

    def locateAnimations(self):
        data = self.segment[0x06]
        self.animation = []
        self.offsetAnims = []
        for i in range(0, len(data), 4):
            if (
                (data[i] == 0) and (data[i + 1] > 1) and
                (data[i + 2] == 0) and (data[i + 3] == 0) and
                (data[i + 4] == 0x06) and
                (((data[i + 5] << 16) | (data[i + 6] << 8) | data[i + 7]) < len(data)) and
                (data[i + 8] == 0x06) and
                (((data[i + 9] << 16) | (data[i + 10] << 8) | data[i + 11]) < len(data)) and
                    (data[i + 14] == 0) and (data[i + 15] == 0)):

                print("        Anims found at %08X" % i, "Frames:", data[i + 1] & 0x00FFFFFF)
                self.animation.extend([i])
                self.offsetAnims.extend([i])
                self.offsetAnims[self.animTotal] = (0x06 << 24) | i
                self.animTotal += 1
        if(self.animTotal > 0):
            print("        Total Anims                   :", self.animTotal)

    def locateExternAnimations(self):
        data = self.segment[0x0F]
        self.animation = []
        self.offsetAnims = []
        for i in range(0, len(data), 4):
            if (
                (data[i] == 0) and (data[i + 1] > 1) and
                (data[i + 2] == 0) and (data[i + 3] == 0) and
                (data[i + 4] == 0x06) and
                (((data[i + 5] << 16) | (data[i + 6] << 8) | data[i + 7]) < len(data)) and
                (data[i + 8] == 0x06) and
                (((data[i + 9] << 16) | (data[i + 10] << 8) | data[i + 11]) < len(data)) and
                    (data[i + 14] == 0) and (data[i + 15] == 0)):

                print("        Ext Anims found at %08X" % i, "Frames:", data[i + 1] & 0x00FFFFFF)
                self.animation.extend([i])
                self.offsetAnims.extend([i])
                self.offsetAnims[self.animTotal] = (0x0F << 24) | i
                self.animTotal += 1
        if(self.animTotal > 0):
            print("        Total Anims                   :", self.animTotal)

    def locateLinkAnimations(self):
        data = self.segment[0x04]
        self.animation = []
        self.offsetAnims = []
        self.animFrames = []
        self.animTotal = -1
        if (len(self.segment[0x04]) > 0):
            if (MajorasAnims):
                for i in range(0xD000, 0xE4F8, 8):
                    self.animTotal += 1
                    self.animation.extend([self.animTotal])
                    self.animFrames.extend([self.animTotal])
                    self.offsetAnims.extend([self.animTotal])
                    self.offsetAnims[self.animTotal] = unpack_from(">L", data, i + 4)[0]
                    self.animFrames[self.animTotal] = unpack_from(">h", data, i)[0]
                    # print("- Animation #", self.animTotal+1, "offset: %07X" % self.offsetAnims[self.animTotal], "frames:", self.animFrames[self.animTotal])
            else:
                for i in range(0x2310, 0x34F8, 8):
                    self.animTotal += 1
                    self.animation.extend([self.animTotal])
                    self.animFrames.extend([self.animTotal])
                    self.offsetAnims.extend([self.animTotal])
                    self.offsetAnims[self.animTotal] = unpack_from(">L", data, i + 4)[0]
                    self.animFrames[self.animTotal] = unpack_from(">h", data, i)[0]
                    # print("- Animation #", self.animTotal+1, "offset: %07X" % self.offsetAnims[self.animTotal], "frames:", self.animFrames[self.animTotal])
        print("       Link has come to town!!!!")
        if ((len(self.segment[0x07]) > 0) and (self.animTotal > 0)):
            self.buildLinkAnimations(self.hierarchy[0], 0)

    def importMap(self):
        data = self.segment[0x03]
        for i in range(0, len(data), 8):
            if (data[i] == 0x0A and data[i + 4] == 0x03):
                mho = (data[i + 5] << 16) | (data[i + 6] << 8) | data[i + 7]
                if (mho < len(data)):
                    type = data[mho]
                    count = data[mho + 1]
                    seg = data[mho + 4]
                    start = (data[mho + 5] << 16) | (data[mho + 6] << 8) | data[mho + 7]
                    end = (data[mho + 9] << 16) | (data[mho + 10] << 8) | data[mho + 11]
                    if (data[mho + 4] == 0x03 and start < end and end < len(data)):
                        if (type == 0):
                            for j in range(start, end, 4):
                                self.buildDisplayList(None, [None], unpack_from(">L", data, j)[0])
                        elif (type == 2):
                            for j in range(start, end, 16):
                                near = (data[j + 8] << 24) | (data[j + 9] << 16) | (data[j + 10] << 8) | data[j + 11]
                                far = (data[j + 12] << 24) | (data[j + 13] << 16) | (data[j + 14] << 8) | data[j + 15]
                                if (near != 0):
                                    self.buildDisplayList(None, [None], near)
                                elif (far != 0):
                                    self.buildDisplayList(None, [None], far)
                return
            elif (data[i] == 0x14):
                break
        print("ERROR:  Map header not found")

    def importObj(self):
        print("\nLocating hierarchies...")
        self.locateHierarchies()
        for hierarchy in self.hierarchy:
            print("\nBuilding hierarchy '%s'..." % hierarchy.name)
            hierarchy.create()
            for i in range(hierarchy.limbCount):
                limb = hierarchy.limb[i]
                if limb.near != 0:
                    if validOffset(self.segment, limb.near):
                        print("   0x%02X : building display lists..." % i)
                        self.resetCombiner()
                        self.buildDisplayList(hierarchy, limb, limb.near)
                    else:
                        print("   0x%02X : out of range" % i)
                else:
                    print("   0x%02X : n/a" % i)
        if len(self.hierarchy) > 0:
            bpy.context.scene.objects.active = self.hierarchy[0].armature
            self.hierarchy[0].armature.select = True
            bpy.ops.object.mode_set(mode='POSE', toggle=False)
            if (AnimtoPlay > 0):
                bpy.context.scene.frame_end = 1
                if(ExternalAnimes and len(self.segment[0x0F]) > 0):
                    self.locateExternAnimations()
                else:
                    self.locateAnimations()
                if len(self.animation) > 0:
                    self.buildAnimations(self.hierarchy[0], 0)
                else:
                    self.locateLinkAnimations()
            else:
                print("   Load anims OFF.")

    def resetCombiner(self):
        self.primColor = Vector([1.0, 1.0, 1.0])
        self.envColor = Vector([1.0, 1.0, 1.0])
        self.vertexColor = Vector([1.0, 1.0, 1.0])
        self.shadeColor = Vector([1.0, 1.0, 1.0])

    def getCombinerColor(self):
        cc = Vector([1.0, 1.0, 1.0])
        if enablePrimColor:
            cc = mulVec(cc, self.primColor)
        if enableEnvColor:
            cc = mulVec(cc, self.envColor)
        if vertexMode == 'COLORS':
            print(self.vertexColor)
            cc = mulVec(cc, self.vertexColor)
        elif vertexMode == 'NORMALS':
            cc = mulVec(cc, self.shadeColor)
        return cc

    def buildDisplayList(self, hierarchy, limb, offset):
        data = self.segment[offset >> 24]
        mesh = Mesh()
        has_tex = False
        material = None
        if hierarchy:
            matrix = [limb]
        else:
            matrix = [None]
        for i in range(offset & 0x00FFFFFF, len(data), 8):
            w0 = unpack_from(">L", data, i)[0]
            w1 = unpack_from(">L", data, i + 4)[0]
            if data[i] == 0x01:
                count = (data[i + 1] << 4) | (data[i + 2] >> 4)
                index = (data[i + 3] >> 1) - count
                offset = unpack_from(">L", data, i + 4)[0]
                if validOffset(self.segment, offset + int(16 * count) - 1):
                    for j in range(count):
                        self.vbuf[index + j].read(self.segment, offset + 16 * j)
                        if hierarchy:
                            self.vbuf[index + j].limb = matrix[len(matrix) - 1]
                            if self.vbuf[index + j].limb:
                                self.vbuf[index + j].pos += self.vbuf[index + j].limb.pos
            elif data[i] == 0x02:
                index = ((data[i + 2] & 0x0F) << 3) | (data[i + 3] >> 1)
                if data[i + 1] == 0x10:
                    self.vbuf[index].normal.x = 0.00781250 * unpack_from("b", data, i + 4)[0]
                    self.vbuf[index].normal.z = 0.00781250 * unpack_from("b", data, i + 5)[0]
                    self.vbuf[index].normal.y = 0.00781250 * unpack_from("b", data, i + 6)[0]
                    self.vbuf[index].color = 0.00392157 * unpack_from("BBBB", data, i + 4)[0]
                elif data[i + 1] == 0x14:
                    self.vbuf[index].uv.x = float(unpack_from(">h", data, i + 4)[0])
                    self.vbuf[index].uv.y = float(unpack_from(">h", data, i + 6)[0])
            elif data[i] == 0x05 or data[i] == 0x06:
                if has_tex:
                    material = None
                    for j in range(len(self.material)):
                        if self.material[j].name == "mtl_%08X" % self.tile[0].data:
                            material = self.material[j]
                            break
                    if material is None:
                        material = self.tile[0].create(self.segment)
                        if material:
                            self.material.extend([material])
                    has_tex = False
                v1, v2 = None, None
                vi1, vi2 = -1, -1
                if not importTextures:
                    material = None
                count = 0
                try:
                    for j in range(1, (data[i] - 4) * 4):
                        if j != 4:
                            v3 = self.vbuf[data[i + j] >> 1]
                            vi3 = -1
                            for k in range(len(mesh.verts)):
                                if mesh.verts[k] == (v3.pos.x, v3.pos.y, v3.pos.z):
                                    vi3 = k
                                    break
                            if vi3 == -1:
                                mesh.verts.extend([(v3.pos.x, v3.pos.y, v3.pos.z)])
                                vi3 = len(mesh.verts) - 1
                                count += 1
                            if j == 1 or j == 5:
                                v1 = v3
                                vi1 = vi3
                            elif j == 2 or j == 6:
                                v2 = v3
                                vi2 = vi3
                            elif j == 3 or j == 7:
                                sc = (((v3.normal.x + v3.normal.y + v3.normal.z) / 3) + 1.0) / 2
                                self.vertexColor = Vector([v3.color[0], v3.color[1], v3.color[2]])
                                self.shadeColor = Vector([sc, sc, sc])
                                mesh.colors.extend([self.getCombinerColor()])
                                sc = (((v2.normal.x + v2.normal.y + v2.normal.z) / 3) + 1.0) / 2
                                self.vertexColor = Vector([v2.color[0], v2.color[1], v2.color[2]])
                                self.shadeColor = Vector([sc, sc, sc])
                                mesh.colors.extend([self.getCombinerColor()])
                                sc = (((v1.normal.x + v1.normal.y + v1.normal.z) / 3) + 1.0) / 2
                                self.vertexColor = Vector([v1.color[0], v1.color[1], v1.color[2]])
                                self.shadeColor = Vector([sc, sc, sc])
                                mesh.colors.extend([self.getCombinerColor()])
                                mesh.uvs.extend([(self.tile[0].offset.x + v3.uv.x * self.tile[0].ratio.x, self.tile[0].offset.y - v3.uv.y * self.tile[0].ratio.y),
                                                (self.tile[0].offset.x + v2.uv.x * self.tile[0].ratio.x, self.tile[0].offset.y - v2.uv.y * self.tile[0].ratio.y),
                                                (self.tile[0].offset.x + v1.uv.x * self.tile[0].ratio.x, self.tile[0].offset.y - v1.uv.y * self.tile[0].ratio.y),
                                                material])
                                if hierarchy:
                                    if v3.limb:
                                        if not (("limb_%02i" % v3.limb.index) in mesh.vgroups):
                                            mesh.vgroups["limb_%02i" % v3.limb.index] = []
                                        mesh.vgroups["limb_%02i" % v3.limb.index].extend([vi3])
                                    if v2.limb:
                                        if not (("limb_%02i" % v2.limb.index) in mesh.vgroups):
                                            mesh.vgroups["limb_%02i" % v2.limb.index] = []
                                        mesh.vgroups["limb_%02i" % v2.limb.index].extend([vi2])
                                    if v1.limb:
                                        if not (("limb_%02i" % v1.limb.index) in mesh.vgroups):
                                            mesh.vgroups["limb_%02i" % v1.limb.index] = []
                                        mesh.vgroups["limb_%02i" % v1.limb.index].extend([vi1])
                                mesh.faces.extend([(vi1, vi2, vi3)])
                except:
                    for i in range(count):
                        mesh.verts.pop()
            elif data[i] == 0xD7:
                pass
            elif data[i] == 0xD8 and enableMatrices:
                if hierarchy and len(matrix) > 1:
                    matrix.pop()
            elif data[i] == 0xDA and enableMatrices:
                if hierarchy and data[i + 4] == 0x0D:
                    if (data[i + 3] & 0x04) == 0:
                        matrixLimb = hierarchy.getMatrixLimb(unpack_from(">L", data, i + 4)[0])
                        if (data[i + 3] & 0x02) == 0:
                            newMatrixLimb = Limb()
                            newMatrixLimb.index = matrixLimb.index
                            newMatrixLimb.pos = (Vector([matrixLimb.pos.x, matrixLimb.pos.y, matrixLimb.pos.z]) + matrix[len(matrix) - 1].pos) / 2
                            matrixLimb = newMatrixLimb
                        if (data[i + 3] & 0x01) == 0:
                            matrix.extend([matrixLimb])
                        else:
                            matrix[len(matrix) - 1] = matrixLimb
                    else:
                        matrix.extend([matrix[len(matrix) - 1]])
                elif hierarchy:
                    print("unknown limb %08X %08X" % (w0, w1))
            elif data[i] == 0xDE:
                mesh.create(hierarchy, offset)
                mesh.__init__()
                offset = (offset >> 24) | i + 8
                if validOffset(self.segment, w1):
                    self.buildDisplayList(hierarchy, limb, w1)
                if data[i + 1] != 0x00:
                    return
            elif data[i] == 0xDF:
                mesh.create(hierarchy, offset)
                return
            elif data[i] == 0xE7:
                mesh.create(hierarchy, offset)
                mesh.__init__()
                offset = (offset >> 24) | i
            elif data[i] == 0xF0:
                self.palSize = ((w1 & 0x00FFF000) >> 13) + 1
            elif data[i] == 0xF2:
                self.tile[self.curTile].rect.x = (w0 & 0x00FFF000) >> 14
                self.tile[self.curTile].rect.y = (w0 & 0x00000FFF) >> 2
                self.tile[self.curTile].rect.z = (w1 & 0x00FFF000) >> 14
                self.tile[self.curTile].rect.w = (w1 & 0x00000FFF) >> 2
                self.tile[self.curTile].width = (self.tile[self.curTile].rect.z - self.tile[self.curTile].rect.x) + 1
                self.tile[self.curTile].height = (self.tile[self.curTile].rect.w - self.tile[self.curTile].rect.y) + 1
                self.tile[self.curTile].texBytes = int(self.tile[self.curTile].width * self.tile[self.curTile].height) << 1
                if (self.tile[self.curTile].texBytes >> 16) == 0xFFFF:
                    self.tile[self.curTile].texBytes = self.tile[self.curTile].size << 16 >> 15
                self.tile[self.curTile].calculateSize()
            elif data[i] == 0xF4 or data[i] == 0xE4 or data[i] == 0xFE or data[i] == 0xFF:
                print("%08X : %08X" % (w0, w1))
            elif data[i] == 0xF5:
                self.tile[self.curTile].texFmt = (w0 >> 16) & 0xFF
                self.tile[self.curTile].txlSize = (w0 >> 19) & 0x03
                self.tile[self.curTile].lineSize = (w0 >> 9) & 0x1F
                self.tile[self.curTile].clip.x = (w1 >> 8) & 0x03
                self.tile[self.curTile].clip.y = (w1 >> 18) & 0x03
                self.tile[self.curTile].mask.x = (w1 >> 4) & 0x0F
                self.tile[self.curTile].mask.y = (w1 >> 14) & 0x0F
                self.tile[self.curTile].tshift.x = w1 & 0x0F
                self.tile[self.curTile].tshift.y = (w1 >> 10) & 0x0F
            elif data[i] == 0xFA:
                self.primColor = Vector([min(0.003922 * ((w1 >> 24) & 0xFF), 1.0), min(0.003922 * ((w1 >> 16) & 0xFF), 1.0), min(0.003922 * ((w1 >> 8) & 0xFF), 1.0)])
            elif data[i] == 0xFB:
                self.envColor = Vector([min(0.003922 * ((w1 >> 24) & 0xFF), 1.0), min(0.003922 * ((w1 >> 16) & 0xFF), 1.0), min(0.003922 * ((w1 >> 8) & 0xFF), 1.0)])
                if invertEnvColor:
                    self.envColor = Vector([1.0, 1.0, 1.0]) - self.envColor
            elif data[i] == 0xFD:
                try:
                    if data[i - 8] == 0xF2:
                        self.curTile = 1
                    else:
                        self.curTile = 0
                except:
                    pass
                try:
                    if data[i + 8] == 0xE8:
                        self.tile[0].palette = w1
                    else:
                        self.tile[self.curTile].data = w1
                except:
                    pass
                has_tex = True

    def LinkTpose(self, hierarchy):
        segment = []
        data = self.segment[0x06]
        segment = self.segment
        RX, RY, RZ = 0, 0, 0
        BoneCount = hierarchy.limbCount
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True
        bonesIndx = [0, -90, 0, 0, 0, 0, 0, 0, 0, 90, 0, 0, 0, 180, 0, 0, -180, 0, 0, 0, 0]
        bonesIndy = [0, 90, 0, 0, 0, 90, 0, 0, 90, -90, -90, -90, 0, 0, 0, 90, 0, 0, 90, 0, 0]
        bonesIndz = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -90, 0, 0, 90, 0, 0, 0, 0]

        print("Link T Pose...")
        for i in range(BoneCount):
            bIndx = ((BoneCount - 1) - i)
            if (i > -1):
                bone = bpy.data.armatures["armature"].bones["limb_%02i" % (bIndx)]
                bone.select = True
                bpy.ops.transform.rotate(value=radians(bonesIndx[bIndx]), axis=(0, 0, 0), constraint_axis=(True, False, False))
                bpy.ops.transform.rotate(value=radians(bonesIndz[bIndx]), axis=(0, 0, 0), constraint_axis=(False, False, True))
                bpy.ops.transform.rotate(value=radians(bonesIndy[bIndx]), axis=(0, 0, 0), constraint_axis=(False, True, False))
                bpy.ops.pose.select_all(action="DESELECT")

        bpy.data.armatures["armature"].bones["limb_00"].select = True  # # Translations
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(True, False, False))
        bpy.ops.transform.translate(value=(0, 0, 50), constraint_axis=(False, False, True))
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, True, False))
        bpy.ops.pose.select_all(action="DESELECT")
        bpy.context.scene.tool_settings.use_keyframe_insert_auto = False

        for i in range(BoneCount):
            bIndx = i
            if (i > -1):
                bone = bpy.data.armatures["armature"].bones["limb_%02i" % (bIndx)]
                bone.select = True
                bpy.ops.transform.rotate(value=radians(-bonesIndy[bIndx]), axis=(0, 0, 0), constraint_axis=(False, True, False))
                bpy.ops.transform.rotate(value=radians(-bonesIndz[bIndx]), axis=(0, 0, 0), constraint_axis=(False, False, True))
                bpy.ops.transform.rotate(value=radians(-bonesIndx[bIndx]), axis=(0, 0, 0), constraint_axis=(True, False, False))
                bpy.ops.pose.select_all(action="DESELECT")

        bpy.data.armatures["armature"].bones["limb_00"].select = True  # # Translations
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(True, False, False))
        bpy.ops.transform.translate(value=(0, 0, -50), constraint_axis=(False, False, True))
        bpy.ops.transform.translate(value=(0, 0, 0), constraint_axis=(False, True, False))
        bpy.ops.pose.select_all(action="DESELECT")

    def buildLinkAnimations(self, hierarchy, newframe):
        global AnimtoPlay
        global Animscount
        segment = []
        rot_indx = 0
        rot_indy = 0
        rot_indz = 0
        data = self.segment[0x06]
        segment = self.segment
        n_anims = self.animTotal
        seg, offset = splitOffset(hierarchy.offset)
        BoneCount = hierarchy.limbCount
        RX, RY, RZ = 0, 0, 0
        frameCurrent = newframe

        if (AnimtoPlay > 0 and AnimtoPlay <= n_anims):
            currentanim = AnimtoPlay - 1
        else:
            currentanim = 0

        print("currentanim:", currentanim + 1, "frameCurrent:", frameCurrent + 1)
        AnimationOffset = self.offsetAnims[currentanim]
        TAnimationOffset = self.offsetAnims[currentanim]
        AniSeg = AnimationOffset >> 24
        AnimationOffset &= 0xFFFFFF
        rot_offset = AnimationOffset
        rot_offset += (frameCurrent * (BoneCount * 6 + 8))
        frameTotal = self.animFrames[currentanim]
        rot_offset += BoneCount * 6

        Trot_offset = TAnimationOffset & 0xFFFFFF
        Trot_offset += (frameCurrent * (BoneCount * 6 + 8))
        TRX = unpack_from(">h", segment[AniSeg], Trot_offset)[0]
        Trot_offset += 2
        TRZ = unpack_from(">h", segment[AniSeg], Trot_offset)[0]
        Trot_offset += 2
        TRY = -unpack_from(">h", segment[AniSeg], Trot_offset)[0]
        Trot_offset += 2
        BoneListListOffset = unpack_from(">L", segment[seg], offset)[0]
        BoneListListOffset &= 0xFFFFFF

        BoneOffset = unpack_from(">L", segment[seg], BoneListListOffset + (0 << 2))[0]
        S_Seg = (BoneOffset >> 24) & 0xFF
        BoneOffset &= 0xFFFFFF
        TRX += unpack_from(">h", segment[S_Seg], BoneOffset)[0]
        TRZ += unpack_from(">h", segment[S_Seg], BoneOffset + 2)[0]
        TRY += -unpack_from(">h", segment[S_Seg], BoneOffset + 4)[0]
        newLocx = TRX / 79
        newLocz = -25.5
        newLocz += TRZ / 79
        newLocy = TRY / 79

        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True

        for i in range(BoneCount):
            # Had to reverse here, cuz didn't find a way to rotate bones on LOCAL space, start rotating from last to first bone on hierarchy GLOBAL.
            bIndx = ((BoneCount - 1) - i)
            RX = unpack_from(">h", segment[AniSeg], rot_offset)[0]
            rot_offset -= 2
            RY = unpack_from(">h", segment[AniSeg], rot_offset + 4)[0]
            rot_offset -= 2
            RZ = unpack_from(">h", segment[AniSeg], rot_offset + 8)[0]
            rot_offset -= 2

            RX /= (182.04444444444444444444)
            RY /= (182.04444444444444444444)
            RZ /= (182.04444444444444444444)

            RXX = (RX)
            RYY = (-RZ)
            RZZ = (RY)

            # print("limb:", bIndx,"RX", int(RXX), "RZ", int(RZZ), "RY", int(RYY), "anim:", currentanim+1, "frame:", frameCurrent+1)
            if (i > -1):
                bone = bpy.data.armatures["armature"].bones["limb_%02i" % (bIndx)]
                bone.select = True
                bpy.ops.transform.rotate(value=radians(RXX), axis=(0, 0, 0), constraint_axis=(True, False, False))
                bpy.ops.transform.rotate(value=radians(RZZ), axis=(0, 0, 0), constraint_axis=(False, False, True))
                bpy.ops.transform.rotate(value=radians(RYY), axis=(0, 0, 0), constraint_axis=(False, True, False))
                bpy.ops.pose.select_all(action="DESELECT")

        bpy.data.armatures["armature"].bones["limb_00"].select = True  # # Translations
        bpy.ops.transform.translate(value=(newLocx, 0, 0), constraint_axis=(True, False, False))
        bpy.ops.transform.translate(value=(0, 0, newLocz), constraint_axis=(False, False, True))
        bpy.ops.transform.translate(value=(0, newLocy, 0), constraint_axis=(False, True, False))
        bpy.ops.pose.select_all(action="DESELECT")

        if (frameCurrent < (frameTotal - 1)):  # # Next Frame ### Could have done some math here but... just reverse previus frame, so it just repose.
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = False

            bpy.data.armatures["armature"].bones["limb_00"].select = True  # # Translations
            bpy.ops.transform.translate(value=(-newLocx, 0, 0), constraint_axis=(True, False, False))
            bpy.ops.transform.translate(value=(0, 0, -newLocz), constraint_axis=(False, False, True))
            bpy.ops.transform.translate(value=(0, -newLocy, 0), constraint_axis=(False, True, False))
            bpy.ops.pose.select_all(action="DESELECT")

            rot_offset = AnimationOffset
            rot_offset += (frameCurrent * (BoneCount * 6 + 8))
            rot_offset += 6
            for i in range(BoneCount):
                RX = unpack_from(">h", segment[AniSeg], rot_offset)[0]
                rot_offset += 2
                RY = unpack_from(">h", segment[AniSeg], rot_offset)[0]
                rot_offset += 2
                RZ = unpack_from(">h", segment[AniSeg], rot_offset)[0]
                rot_offset += 2

                RX /= (182.04444444444444444444)
                RY /= (182.04444444444444444444)
                RZ /= (182.04444444444444444444)

                RXX = (-RX)
                RYY = (RZ)
                RZZ = (-RY)

                # print("limb:", i,"RX", int(RXX), "RZ", int(RZZ), "RY", int(RYY), "anim:", currentanim+1, "frame:", frameCurrent+1)
                if (i > -1):
                    bone = bpy.data.armatures["armature"].bones["limb_%02i" % (i)]
                    bone.select = True
                    bpy.ops.transform.rotate(value=radians(RYY), axis=(0, 0, 0), constraint_axis=(False, True, False))
                    bpy.ops.transform.rotate(value=radians(RZZ), axis=(0, 0, 0), constraint_axis=(False, False, True))
                    bpy.ops.transform.rotate(value=radians(RXX), axis=(0, 0, 0), constraint_axis=(True, False, False))
                    bpy.ops.pose.select_all(action="DESELECT")

            bpy.context.scene.frame_end += 1
            bpy.context.scene.frame_current += 1
            frameCurrent += 1
            self.buildLinkAnimations(hierarchy, frameCurrent)
        else:
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = False
            bpy.context.scene.frame_current = 1

    def buildAnimations(self, hierarchy, newframe):
        segment = []
        rot_indx = 0
        rot_indy = 0
        rot_indz = 0
        Trot_indx = 0
        Trot_indy = 0
        Trot_indz = 0
        data = self.segment[0x06]
        segment = self.segment
        RX, RY, RZ = 0, 0, 0
        rot_valsx = [0x2000]
        n_anims = self.animTotal
        if (AnimtoPlay > 0 and AnimtoPlay <= n_anims):
            currentanim = AnimtoPlay - 1
        else:
            currentanim = 0

        AnimationOffset = self.offsetAnims[currentanim]
        seg, offset = splitOffset(hierarchy.offset)
        BoneCount = hierarchy.limbCount
        frameCurrent = newframe

        if not validOffset(segment, AnimationOffset):
            return

        AniSeg = AnimationOffset >> 24
        AnimationOffset &= 0xFFFFFF

        frameTotal = unpack_from(">h", segment[AniSeg], (AnimationOffset))[0]
        rot_vals_addr = unpack_from(">L", segment[AniSeg], (AnimationOffset + 4))[0]
        RotIndexoffset = unpack_from(">L", segment[AniSeg], (AnimationOffset + 8))[0]
        Limit = unpack_from(">h", segment[AniSeg], (AnimationOffset + 12))[0]

        rot_vals_n = int((RotIndexoffset - rot_vals_addr) / 2)
        rot_vals_addr &= 0xFFFFFF
        RotIndexoffset &= 0xFFFFFF

        bpy.context.scene.tool_settings.use_keyframe_insert_auto = True
        bpy.context.scene.frame_end = frameTotal
        bpy.context.scene.frame_current = frameCurrent + 1

        print("currentanim:", currentanim + 1, "frameCurrent:", frameCurrent + 1)
        for j in range(rot_vals_n):
            rot_valsx.extend([j])
            rot_valsx[j] = unpack_from(">h", segment[AniSeg], (rot_vals_addr) + (j * 2))[0]

        # # Translations
        Trot_indexx = unpack_from(">h", segment[AniSeg], RotIndexoffset)[0]
        Trot_indexy = unpack_from(">h", segment[AniSeg], RotIndexoffset + 2)[0]
        Trot_indexz = unpack_from(">h", segment[AniSeg], RotIndexoffset + 4)[0]

        Trot_indx = Trot_indexx
        Trot_indz = Trot_indexz
        Trot_indy = Trot_indexy

        if (Trot_indx >= Limit):
            Trot_indx += frameCurrent
        if (Trot_indz >= Limit):
            Trot_indz += frameCurrent
        if (Trot_indy >= Limit):
            Trot_indy += frameCurrent

        TRX = rot_valsx[Trot_indx]
        TRZ = rot_valsx[Trot_indy]
        TRY = rot_valsx[Trot_indz]

        newLocx = TRX / 79
        newLocz = 10
        newLocz += TRZ / 79
        newLocy = -TRY / 79
        # print("X",int(TRX),"Y",int(TRZ),"Z",int(TRY))

        # print("       ",frameTotal, "Frames", Limit, "still values", ((rot_vals_n - Limit) / frameTotal), "tracks\n" )
        for i in range(BoneCount):
            bIndx = ((BoneCount - 1) - i)  # Had to reverse here, cuz didn't find a way to rotate bones on LOCAL space, start rotating from last to first bone on hierarchy GLOBAL.
            rot_indexx = unpack_from(">h", segment[AniSeg], RotIndexoffset + (bIndx * 6) + 6)[0]
            rot_indexy = unpack_from(">h", segment[AniSeg], RotIndexoffset + (bIndx * 6) + 8)[0]
            rot_indexz = unpack_from(">h", segment[AniSeg], RotIndexoffset + (bIndx * 6) + 10)[0]

            rot_indx = rot_indexx
            rot_indy = rot_indexy
            rot_indz = rot_indexz

            if (rot_indx >= Limit):
                rot_indx += frameCurrent
            if (rot_indy >= Limit):
                rot_indy += frameCurrent
            if (rot_indz >= Limit):
                rot_indz += frameCurrent

            RX = rot_valsx[rot_indx] / 182.04444444444444444444
            RY = -rot_valsx[rot_indz] / 182.04444444444444444444
            RZ = rot_valsx[rot_indy] / 182.04444444444444444444

            RXX = radians(RX)
            RYY = radians(RY)
            RZZ = radians(RZ)

            # print("limb:", bIndx, "XIdx:", rot_indexx, "YIdx:", rot_indexy , "ZIdx:", rot_indexz, "frameTotal:", frameTotal)
            # print("limb:", bIndx,"RX", int(RX), "RZ", int(RZ), "RY", int(RY), "anim:", currentanim+1, "frame:", frameCurrent+1, "frameTotal:", frameTotal)
            if (bIndx > -1):
                bone = bpy.data.armatures["armature"].bones["limb_%02i" % (bIndx)]
                bone.select = True
                bpy.ops.transform.rotate(value=RXX, axis=(0, 0, 0), constraint_axis=(True, False, False))
                bpy.ops.transform.rotate(value=RZZ, axis=(0, 0, 0), constraint_axis=(False, False, True))
                bpy.ops.transform.rotate(value=RYY, axis=(0, 0, 0), constraint_axis=(False, True, False))
                bpy.ops.pose.select_all(action="DESELECT")

        bpy.data.armatures["armature"].bones["limb_00"].select = True  # # Translations
        bpy.ops.transform.translate(value=(newLocx, 0, 0), constraint_axis=(True, False, False))
        bpy.ops.transform.translate(value=(0, 0, newLocz), constraint_axis=(False, False, True))
        bpy.ops.transform.translate(value=(0, newLocy, 0), constraint_axis=(False, True, False))
        bpy.ops.pose.select_all(action="DESELECT")

        if (frameCurrent < (frameTotal - 1)):  # # Next Frame ### Could have done some math here but... just reverse previus frame, so it just repose.
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = False

            bpy.data.armatures["armature"].bones["limb_00"].select = True  # # Translations
            bpy.ops.transform.translate(value=(-newLocx, 0, 0), constraint_axis=(True, False, False))
            bpy.ops.transform.translate(value=(0, 0, -newLocz), constraint_axis=(False, False, True))
            bpy.ops.transform.translate(value=(0, -newLocy, 0), constraint_axis=(False, True, False))
            bpy.ops.pose.select_all(action="DESELECT")

            for i in range(BoneCount):
                bIndx = i
                rot_indexx = unpack_from(">h", segment[AniSeg], RotIndexoffset + (bIndx * 6) + 6)[0]
                rot_indexy = unpack_from(">h", segment[AniSeg], RotIndexoffset + (bIndx * 6) + 8)[0]
                rot_indexz = unpack_from(">h", segment[AniSeg], RotIndexoffset + (bIndx * 6) + 10)[0]

                rot_indx = rot_indexx
                rot_indy = rot_indexy
                rot_indz = rot_indexz

                if (rot_indx > Limit):
                    rot_indx += frameCurrent
                if (rot_indy > Limit):
                    rot_indy += frameCurrent
                if (rot_indz > Limit):
                    rot_indz += frameCurrent

                RX = -rot_valsx[rot_indx] / 182.04444444444444444444
                RY = rot_valsx[rot_indz] / 182.04444444444444444444
                RZ = -rot_valsx[rot_indy] / 182.04444444444444444444

                RXX = radians(RX)
                RYY = radians(RY)
                RZZ = radians(RZ)

                # print("limb:", i, "XIdx:", rot_indexx, "YIdx:", rot_indexy , "ZIdx:", rot_indexz, "frameTotal:", frameTotal)
                # print("limb:", bIndx,"RX", int(RX), "RZ", int(RZ), "RY", int(RY), "anim:", currentanim+1, "frame:", frameCurrent+1, "frameTotal:", frameTotal)
                if (bIndx > -1):
                    bone = bpy.data.armatures["armature"].bones["limb_%02i" % (bIndx)]
                    bone.select = True
                    bpy.ops.transform.rotate(value=RYY, axis=(0, 0, 0), constraint_axis=(False, True, False))
                    bpy.ops.transform.rotate(value=RZZ, axis=(0, 0, 0), constraint_axis=(False, False, True))
                    bpy.ops.transform.rotate(value=RXX, axis=(0, 0, 0), constraint_axis=(True, False, False))
                    bpy.ops.pose.select_all(action="DESELECT")

            frameCurrent += 1
            self.buildAnimations(hierarchy, frameCurrent)
        else:
            bpy.context.scene.tool_settings.use_keyframe_insert_auto = False
            bpy.context.scene.frame_current = 1

global Animscount
Animscount = 1


class ImportZ64(bpy.types.Operator, ImportHelper):
    """Load a Zelda64 File"""
    bl_idname = "file.zobj"
    bl_label = "Import Zelda64"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".zobj"

    filter_glob = StringProperty(default="*.zobj;*.zmap", options={'HIDDEN'})

    loadOtherSegments = BoolProperty(
        name="Load Data From Other Segments",
        description="Load data from other segments",
        default=True)

    vertexMode = EnumProperty(
        name="Vtx Mode",
        items=(
            ('COLORS', "COLORS", "Use vertex colors"),
            ('NORMALS', "NORMALS", "Use vertex normals as shading"),
            ('NONE', "NONE", "Don't use vertex colors or normals")
        ),
        default='NORMALS')

    enableMatrices = BoolProperty(
        name="Matrices",
        description="Enable texture mirroring",
        default=True)

    enablePrimColor = BoolProperty(
        name="Prim Color",
        description="Enable blending with primitive color",
        default=True)

    enableEnvColor = BoolProperty(
        name="Env Color",
        description="Enable blending with environment color",
        default=True)

    invertEnvColor = BoolProperty(
        name="Invert Env Color",
        description="Invert environment color (temporary fix)",
        default=False)

    exportTextures = BoolProperty(
        name="Export Textures",
        description="Export textures for the model",
        default=True)

    importTextures = BoolProperty(
        name="Import Textures",
        description="Import textures for the model",
        default=True)

    enableTexClamp = BoolProperty(
        name="Texture Clamp",
        description="Enable texture clamping",
        default=True)

    enableTexMirror = BoolProperty(
        name="Texture Mirror",
        description="Enable texture mirroring",
        default=True)

    enableToon = BoolProperty(
        name="Toony UVs",
        description="Obtain a toony effect by not scaling down the uv coords",
        default=False)

    AnimtoPlay = IntProperty(
        name="Anim",
        description="Choose an anim to Play, if < 1 don't load anims.",
        default=1)

    MajorasAnims = BoolProperty(
        name="MajorasAnims",
        description="Majora's Mask Link's Anims.",
        default=False)

    ExternalAnimes = BoolProperty(
        name="ExternalAnimes",
        description="Load External Animes.",
        default=False)

    def execute(self, context):
        global fpath
        fpath, fext = os.path.splitext(self.filepath)
        fpath, fname = os.path.split(fpath)
        global vertexMode, enableMatrices
        global enablePrimColor, enableEnvColor, invertEnvColor
        global importTextures, exportTextures
        global enableTexClamp, enableTexMirror
        global enableMatrices, enableToon
        global AnimtoPlay, MajorasAnims, ExternalAnimes
        vertexMode = self.vertexMode
        enableMatrices = self.enableMatrices
        enablePrimColor = self.enablePrimColor
        enableEnvColor = self.enableEnvColor
        invertEnvColor = self.invertEnvColor
        importTextures = self.importTextures
        exportTextures = self.exportTextures
        enableTexClamp = self.enableTexClamp
        enableTexMirror = self.enableTexMirror
        enableToon = self.enableToon
        AnimtoPlay = self.AnimtoPlay
        MajorasAnims = self.MajorasAnims
        ExternalAnimes = self.ExternalAnimes

        print("Importing '%s'..." % fname)
        time_start = time.time()
        f3dzex = F3DZEX()
        if self.loadOtherSegments:
            for i in range(16):
                # f3dzex.setSegment(i, fpath + "/segment_%02X.zdata" % i)
                f3dzex.setSegment(i, os.path.join(fpath, "segment_%02X.zdata" % i))

        if fext.lower() == '.zmap':
            f3dzex.setSegment(0x03, self.filepath)
            f3dzex.importMap()
        else:
            f3dzex.setSegment(0x06, self.filepath)
            f3dzex.importObj()
        print("SUCCESS:  Elapsed time %.4f sec" % (time.time() - time_start))
        bpy.context.scene.update()
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "vertexMode")
        row = layout.row(align=True)
        row.prop(self, "loadOtherSegments")
        box = layout.box()
        row = box.row(align=True)
        row.prop(self, "enableMatrices")
        row.prop(self, "enablePrimColor")
        row = box.row(align=True)
        row.prop(self, "enableEnvColor")
        row.prop(self, "invertEnvColor")
        row = box.row(align=True)
        row.prop(self, "exportTextures")
        row.prop(self, "importTextures")
        row = box.row(align=True)
        row.prop(self, "enableTexClamp")
        row.prop(self, "enableTexMirror")
        row = box.row(align=True)
        row.prop(self, "enableToon")
        row = box.row(align=True)
        row.prop(self, "AnimtoPlay")
        row = box.row(align=True)
        row.prop(self, "MajorasAnims")
        row.prop(self, "ExternalAnimes")


def menu_func_import(self, context):
    self.layout.operator(ImportZ64.bl_idname, text="Zelda64 (.zobj;.zmap)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
