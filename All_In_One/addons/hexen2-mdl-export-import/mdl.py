# vim:ts=4:et
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

# <pep8 compliant>

from struct import unpack, pack

class MDL:
    ST_SYNC = 0
    ST_RAND = 1
    SYNCTYPE={'ST_SYNC':ST_SYNC, 'ST_RAND':ST_RAND,
              ST_SYNC:'ST_SYNC', ST_RAND:'ST_RAND'}
    EF_ROCKET = 1
    EF_GRENADE = 2
    EF_GIB = 4
    EF_ROTATE = 8
    EF_TRACER = 16
    EF_ZOMGIB = 32
    EF_TRACER2 = 64
    EF_TRACER3 = 128
    EFFECTS={'EF_NONE':0, 'EF_ROCKET':EF_ROCKET, 'EF_GRENADE':EF_GRENADE,
             'EF_GIB':EF_GIB, 'EF_TRACER':EF_TRACER, 'EF_ZOMGIB':EF_ZOMGIB,
             'EF_TRACER2':EF_TRACER2, 'EF_TRACER3':EF_TRACER3}

    class Skin:
        def __init__(self):
            self.name = ''
        def info(self):
            info={}
            if self.type:
                if self.times:
                    info['intervals'] = list(map(lambda t: str(t), self.times))
                info['skins'] = []
                for s in self.skins:
                    info['skins'].append(s.info())
            if self.name:
                info['name'] = self.name
            return info
        def read(self, mdl, sub=0):
            self.width, self.height = mdl.skinwidth, mdl.skinheight
            if sub:
                self.type = 0
                self.read_pixels(mdl)
                return self
            self.type = mdl.read_int()
            if self.type:
                # skin group
                num = mdl.read_int()
                self.times = mdl.read_float(num)
                self.skins = []
                for i in range(num):
                    self.skins.append(MDL.Skin().read(mdl, 1))
                    num -= 1
                return self
            self.read_pixels(mdl)
            return self
        def write(self, mdl, sub=0):
            if not sub:
                mdl.write_int(self.type)
                if self.type:
                    mdl.write_int(len(self.skins))
                    mdl.write_float(self.times)
                    for subskin in self.skins:
                        subskin.write(mdl, 1)
                    return
            mdl.write_bytes(self.pixels)
        def read_pixels(self, mdl):
            size = self.width * self.height
            self.pixels = mdl.read_bytes(size)

    class STVert:
        def __init__(self, st=None, onseam=False):
            if not st:
                st = (0, 0)
            self.onseam = onseam
            self.s, self.t = st
            pass
        def read(self, mdl):
            self.onseam = mdl.read_int()
            self.s, self.t = mdl.read_int(2)
            return self
        def write(self, mdl):
            mdl.write_int(self.onseam)
            mdl.write_int((self.s, self.t))

    class Tri:
        def __init__(self, verts=None, facesfront=True):
            if not verts:
                verts = (0, 0, 0)
            self.facesfront = facesfront
            self.verts = verts
        def read(self, mdl):
            self.facesfront = mdl.read_int()
            self.verts = mdl.read_int(3)
            return self
        def write(self, mdl):
            mdl.write_int(self.facesfront)
            mdl.write_int(self.verts)

    class Frame:
        def __init__(self):
            self.type = 0
            self.name = ""
            self.mins = [0, 0, 0]
            self.maxs = [0, 0, 0]
            self.verts = []
            self.frames = []
            self.times = []
        def info(self):
            info={}
            if self.type:
                if self.times:
                    info['intervals'] = list(map(lambda t: str(t), self.times))
                info['frames'] = []
                for f in self.frames:
                    info['frames'].append(f.info())
            if hasattr(self, 'frameno'):
                info['frameno'] = str(self.frameno)
            if self.name:
                info['name'] = self.name
            return info
        def add_vert(self, vert):
            self.verts.append(vert)
            for i, v in enumerate(vert.r):
                self.mins[i] = min(self.mins[i], v)
                self.maxs[i] = max(self.maxs[i], v)
        def add_frame(self, frame, time):
            self.type = 1
            self.frames.append(frame)
            self.times.append(time)
            for i in range(3):
                self.mins[i] = min(self.mins[i], frame.mins[i])
                self.maxs[i] = max(self.maxs[i], frame.maxs[i])
        def scale(self, mdl):
            self.mins = tuple(map(lambda x, s, t: int((x - t) / s),
                                  self.mins, mdl.scale, mdl.scale_origin))
            self.maxs = tuple(map(lambda x, s, t: int((x - t) / s),
                                  self.maxs, mdl.scale, mdl.scale_origin))
            if self.type:
                for subframe in self.frames:
                    subframe.scale(mdl)
            else:
                for vert in self.verts:
                    vert.scale(mdl)
        def read(self, mdl, numverts, sub=0):
            if sub:
                self.type = 0
            else:
                self.type = mdl.read_int()
            if self.type:
                num = mdl.read_int()
                self.read_bounds(mdl)
                self.times = mdl.read_float(num)
                self.frames = []
                for i in range(num):
                    self.frames.append(MDL.Frame().read(mdl, numverts, 1))
                return self
            self.read_bounds(mdl)
            self.read_name(mdl)
            self.read_verts(mdl, numverts)
            return self
        def write(self, mdl, sub=0):
            if not sub:
                mdl.write_int(self.type)
                if self.type:
                    mdl.write_int(len(self.frames))
                    self.write_bounds(mdl)
                    mdl.write_float(self.times)
                    for frame in self.frames:
                        frame.write(mdl, 1)
                    return
            self.write_bounds(mdl)
            self.write_name(mdl)
            self.write_verts(mdl)
        def read_name(self, mdl):
            if mdl.version == 6:
                name = mdl.read_string(16)
            else:
                name = ""
            if "\0" in name:
                name = name[:name.index("\0")]
            self.name = name
        def write_name(self, mdl):
            if mdl.version == 6:
                mdl.write_string(self.name, 16)
        def read_bounds(self, mdl):
            self.mins = mdl.read_byte(4)[:3]    #discard normal index
            self.maxs = mdl.read_byte(4)[:3]    #discard normal index
        def write_bounds(self, mdl):
            mdl.write_byte(self.mins + (0,))
            mdl.write_byte(self.maxs + (0,))
        def read_verts(self, mdl, num):
            self.verts = []
            for i in range(num):
                self.verts.append(MDL.Vert().read(mdl))
            if mdl.ident == 'MD16':
                for i in range(num):
                    v = MDL.Vert().read(mdl)
                    r = tuple(map(lambda a, b: a + b / 256.0,
                                  self.verts[i].r, v.r))
                    self.verts[i].r = r
        def write_verts(self, mdl):
            for vert in self.verts:
                vert.write(mdl, True)
            if mdl.ident == 'MD16':
                for vert in self.verts:
                    vert.write(mdl, False)

    class Vert:
        def __init__(self, r=None, ni=0):
            if not r:
                r = (0, 0, 0)
            self.r = r
            self.ni = ni
            pass
        def read(self, mdl):
            self.r = mdl.read_byte(3)
            self.ni = mdl.read_byte()
            return self
        def write(self, mdl, high=True):
            if mdl.ident == 'MD16' and not high:
                r = tuple(map(lambda a: int(a * 256) & 255, self.r))
            else:
                r = tuple(map(lambda a: int(a) & 255, self.r))
            mdl.write_byte(r)
            mdl.write_byte(self.ni)
        def scale(self, mdl):
            self.r = tuple(map(lambda x, s, t: (x - t) / s,
                               self.r, mdl.scale, mdl.scale_origin))

    def read_byte(self, count=1):
        size = 1 * count
        data = self.file.read(size)
        data = unpack("<%dB" % count, data)
        if count == 1:
            return data[0]
        return data

    def read_int(self, count=1):
        size = 4 * count
        data = self.file.read(size)
        data = unpack("<%di" % count, data)
        if count == 1:
            return data[0]
        return data

    def read_float(self, count=1):
        size = 4 * count
        data = self.file.read(size)
        data = unpack("<%df" % count, data)
        if count == 1:
            return data[0]
        return data

    def read_bytes(self, size):
        return self.file.read(size)

    def read_string(self, size):
        data = self.file.read(size)
        s = ""
        for c in data:
            s = s + chr(c)
        return s

    def write_byte(self, data):
        if not hasattr(data, "__len__"):
            data = (data,)
        self.file.write(pack(("<%dB" % len(data)), *data))

    def write_int(self, data):
        if not hasattr(data, "__len__"):
            data = (data,)
        self.file.write(pack(("<%di" % len(data)), *data))

    def write_float(self, data):
        if not hasattr(data, "__len__"):
            data = (data,)
        self.file.write(pack(("<%df" % len(data)), *data))

    def write_bytes(self, data, size=-1):
        if size == -1:
            size = len(data)
        self.file.write(data[:size])
        if size > len(data):
            self.file.write(bytes(size - len(data)))

    def write_string(self, data, size=-1):
        data = data.encode()
        self.write_bytes(data, size)

    def __init__(self, name = "mdl", md16 = False):
        self.name = name
        self.ident = md16 and "MD16" or "IDPO"
        self.version = 6        #write only version 6 (nothing usable uses 3)
        self.scale = (1.0, 1.0, 1.0)        #FIXME
        self.scale_origin = (0.0, 0.0, 0.0) #FIXME
        self.boundingradius = 1.0           #FIXME
        self.eyeposition = (0.0, 0.0, 0.0)  #FIXME
        self.synctype = MDL.ST_SYNC
        self.flags = 0          #FIXME config
        self.size = 0           #FIXME ???
        self.skins = []
        self.stverts = []
        self.tris = []
        self.frames = []
        pass
    def read(self, filepath):
        self.file = open(filepath, "rb")
        self.name = filepath.split('/')[-1]
        self.name = self.name.split('.')[0]
        self.ident = self.read_string(4)
        self.version = self.read_int()
        if self.ident not in ["IDPO", "MD16"] or self.version not in [3, 6]:
            return None
        self.scale = self.read_float(3)
        self.scale_origin = self.read_float(3)
        self.boundingradius = self.read_float()
        self.eyeposition = self.read_float(3)
        numskins = self.read_int()
        self.skinwidth, self.skinheight = self.read_int(2)
        numverts, numtris, numframes = self.read_int(3)
        self.synctype = self.read_int()
        if self.version == 6:
            self.flags = self.read_int()
            self.size = self.read_float()
        # read in the skin data
        self.skins = []
        for i in range(numskins):
            self.skins.append(MDL.Skin().read(self))
        #read in the st verts (uv map)
        self.stverts = []
        for i in range(numverts):
            self.stverts.append(MDL.STVert().read(self))
        #read in the tris
        self.tris = []
        for i in range(numtris):
            self.tris.append(MDL.Tri().read(self))
        #read in the frames
        self.frames = []
        for i in range(numframes):
            self.frames.append(MDL.Frame().read(self, numverts))
        return self

    def write(self, filepath):
        self.file = open(filepath, "wb")
        self.write_string(self.ident, 4)
        self.write_int(self.version)
        self.write_float(self.scale)
        self.write_float(self.scale_origin)
        self.write_float(self.boundingradius)
        self.write_float(self.eyeposition)
        self.write_int(len(self.skins))
        self.write_int((self.skinwidth, self.skinheight))
        self.write_int(len(self.stverts))
        self.write_int(len(self.tris))
        self.write_int(len(self.frames))
        self.write_int(self.synctype)
        if self.version == 6:
            self.write_int(self.flags)
            self.write_float(self.size)
        # write out the skin data
        for skin in self.skins:
            skin.write(self)
        #write out the st verts (uv map)
        for stvert in self.stverts:
            stvert.write(self)
        #write out the tris
        for tri in self.tris:
            tri.write(self)
        #write out the frames
        for frame in self.frames:
            frame.write(self)
