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

from math import ceil, cos, log, pi, sin, sqrt
import bpy
from mathutils import Vector
try:
    # 2.57
    from add_object_utils import object_data_add
except:
    # 2.58 +
    from bpy_extras.object_utils import object_data_add


# Create a new mesh (object) from verts/edges/faces.
# verts/edges/faces ... List of vertices/edges/faces for the
#                       new mesh (as used in from_pydata).
# name ... Name of the new mesh (& object).
def create_mesh_object(context, verts, edges, faces, name, operator=None):

    # Create new mesh
    mesh = bpy.data.meshes.new(name)

    # Make a mesh from a list of verts/edges/faces.
    mesh.from_pydata(verts, edges, faces)

    # Update mesh geometry after adding stuff.
    mesh.update()

    return object_data_add(context, mesh, operator)


# A very simple "bridge" tool.
# Connects two equally long vertex rows with faces.
# Returns a list of the new faces (list of  lists)
#
# vertIdx1 ... First vertex list (list of vertex indices).
# vertIdx2 ... Second vertex list (list of vertex indices).
# closed ... Creates a loop (first & last are closed).
# flipped ... Invert the normal of the face(s).
#
# Note: You can set vertIdx1 to a single vertex index to create
#       a fan/star of faces.
# Note: If both vertex idx list are the same length they have
#       to have at least 2 vertices.
def createFaces(vertIdx1, vertIdx2, closed=False, flipped=False):
    faces = []

    if not vertIdx1 or not vertIdx2:
        return None

    if len(vertIdx1) < 2 and len(vertIdx2) < 2:
        return None

    fan = False
    if (len(vertIdx1) != len(vertIdx2)):
        if (len(vertIdx1) == 1 and len(vertIdx2) > 1):
            fan = True
        else:
            return None

    total = len(vertIdx2)

    if closed:
        # Bridge the start with the end.
        if flipped:
            face = [
                vertIdx1[0],
                vertIdx2[0],
                vertIdx2[total - 1]]
            if not fan:
                face.append(vertIdx1[total - 1])
            faces.append(face)

        else:
            face = [vertIdx2[0], vertIdx1[0]]
            if not fan:
                face.append(vertIdx1[total - 1])
            face.append(vertIdx2[total - 1])
            faces.append(face)

    # Bridge the rest of the faces.
    for num in range(total - 1):
        if flipped:
            if fan:
                face = [vertIdx2[num], vertIdx1[0], vertIdx2[num + 1]]
            else:
                face = [vertIdx2[num], vertIdx1[num],
                    vertIdx1[num + 1], vertIdx2[num + 1]]
            faces.append(face)
        else:
            if fan:
                face = [vertIdx1[0], vertIdx2[num], vertIdx2[num + 1]]
            else:
                face = [vertIdx1[num], vertIdx2[num],
                    vertIdx2[num + 1], vertIdx1[num + 1]]
            faces.append(face)

    return faces


def markSeams(mesh, seams):
    for edge in [e for e in mesh.edges if e.key in seams]:
        edge.use_seam = True


def is_active(object):
    if 'sculptie' in object.data.uv_textures:
        img = object.data.uv_textures['sculptie'].data[0].image
        return img is not None
    return False


def check_clean(x, y, u, v, clean):
    '''Returns true if the U, V size with the clean setting aligns to the
    sculptie points on an X, Y sized image'''
    xs, ys = map_pixels(x, y, [3])
    if clean:
        w = int(pow(2, 1 + ceil(log(u) / log(2))) / 2)
        h = int(pow(2, 1 + ceil(log(v) / log(2))) / 2)
    else:
        w = u
        h = v
    for i in range(1, w):
        if int(x * i / float(w)) not in xs:
            return False
    for i in range(1, h):
        if int(y * i / float(h)) not in ys:
            return False
    return True


def face_count(width, height, x_faces, y_faces, model=True):
    '''Returns usable face count from input

    width - sculpt map width
    height - sculpt map width
    x_faces - desired x face count
    y_faces - desired y face count
    model - when true, returns 8 x 4 instead of 9 x 4 to give extra subdivision
    '''
    ratio = float(width) / float(height)
    verts = int(min(0.25 * width * height, x_faces * y_faces))
    if (width != height) and model:
        verts = verts & 0xfff8
    y_faces = int(sqrt(verts / ratio))
    y_faces = max(y_faces, 4)
    x_faces = verts // y_faces
    x_faces = max(x_faces, 4)
    y_faces = verts // x_faces
    return int(x_faces), int(y_faces)


def lod_size(width, height, lod):
    '''Returns x and y face counts for the given map size and lod'''
    sides = float([6, 8, 16, 32][lod])
    ratio = float(width) / float(height)
    verts = int(min(0.25 * width * height, sides * sides))
    y_faces = int(sqrt(verts / ratio))
    y_faces = max(y_faces, 4)
    x_faces = verts // y_faces
    x_faces = max(x_faces, 4)
    y_faces = verts // x_faces
    return int(x_faces), int(y_faces)


def map_pixels(width, height, levels=[3, 2, 1, 0]):
    '''Returns ss and ts as lists of used pixels for the given map size.'''
    ss = [width - 1]
    ts = [height - 1]
    for i in levels:
        u, v = lod_size(width, height, i)
        for p in vertex_pixels(width, u):
            if p not in ss:
                ss.append(p)
        for p in vertex_pixels(height, v):
            if p not in ts:
                ts.append(p)
    ss.sort()
    ts.sort()
    return ss, ts


def map_size(x_faces, y_faces, levels):
    '''Suggests optimal sculpt map size for x_faces * y_faces * levels

    x_faces - x face count
    y_faces - y face count
    levels - subdivision levels

    returns

    s, t, w, h, cs, ct

    s - x face count
    t - y face count
    w - map width
    h - map height
    cs - True if x face count was corrected
    ct - True if y face count was corrected
    '''
    if (((x_faces == 9 and y_faces == 4) or (x_faces == 4 and y_faces == 9))
        and levels == 0):
        s = x_faces
        t = y_faces
        w = (x_faces - x_faces % 2) * 2
        h = (y_faces - y_faces % 2) * 2
        cs = ct = False
    else:
        try:
            w = int(pow(2, levels + 1 + ceil(log(x_faces) / log(2))))
        except OverflowError:
            w = 256
        try:
            h = int(pow(2, levels + 1 + ceil(log(y_faces) / log(2))))
        except OverflowError:
            h = 256
        while (w * h) > 8192:
            w = w / 2
            h = h / 2
        w, h = face_count(w, h, 32, 32)
        if w == 0:
            w = 1
        if h == 0:
            h = 1
        s = min(w, x_faces)
        t = min(h, y_faces)
        levs = levels
        while levs and (w * h * pow(2, levs) > 1024):
            levs -= 1
        w = int(pow(2, levs + 1 + ceil(log(w >> levs) / log(2))))
        h = int(pow(2, levs + 1 + ceil(log(h >> levs) / log(2))))
        cs = True
        ct = True
        if (s << (levels + 1) > w):
            s = w >> (levels + 1)
        if (t << (levels + 1) > h):
            t = h >> (levels + 1)
        if (s < x_faces):
            cs = False
        if (t < y_faces):
            ct = False
    return s, t, w, h, cs, ct


def vertex_pixels(size, faces):
    '''Returns a list of pixels used for vertex points on map size'''
    pixels = [int(size * i / float(faces)) for i in range(faces)]
    pixels.append(size - 1)
    return pixels


class ImageImportSculpty(bpy.types.Operator):
    bl_idname = "image.import_sculpty"
    bl_label = "Import as Sculpty"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        try:
            # use try to catch out of context polls
            ima = context.space_data.image
            if ima is None:
                return False
            return ima.has_data
        except:
            return False

    def execute(self, context):
        image = ImageBuffer(context.space_data.image, clear=False)
        image.add_as_object()
        return {'FINISHED'}


class ImageRenderLOD(bpy.types.Operator):
    bl_idname = "image.sculpty_render_lod"
    bl_label = "Render LOD map"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        try:
            # use try to catch out of context polls
            ima = context.space_data.image
            if ima is None:
                return False
            uv = context.active_object.data.uv_textures.active
        except:
            return False
        if uv is None:
            return False
        return (uv.name == 'sculptie')

    def execute(self, context):
        image = ImageBuffer(context.space_data.image)
        image.render_lod()
        image.update()
        return{'FINISHED'}


class ImageBakeSculpty(bpy.types.Operator):
    bl_idname = "image.sculpty_bake"
    bl_label = "Bake Sculpt Map"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        try:
            # use try to catch out of context polls
            ima = context.space_data.image
            if ima is None:
                return False
            uv = context.active_object.data.uv_textures.active
        except:
            return False
        if uv is None:
            return False
        return (uv.name == 'sculptie')

    def execute(self, context):
        if bake(context.active_object, context.scene):
            return {'FINISHED'}
        return {'CANCELLED'}


class Colour:
    def __init__(self, r=0.0, g=0.0, b=0.0, a=None, colour=None):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        if colour:
            self.r = colour[0]
            self.g = colour[1]
            self.b = colour[2]
            if len(colour) > 3:
                self.a = colour[3]
        if self.a is None:
                self.a = 1.0

    def __sub__(self, other):
        return Colour(
            self.r - other.r,
            self.g - other.g,
            self.b - other.b,
            self.a - other.a)

    def __add__(self, other):
        return Colour(
            self.r + other.r,
            self.g + other.g,
            self.b + other.b,
            self.a + other.a)

    def __mul__(self, scalar):
        return Colour(
            self.r * scalar,
            self.g * scalar,
            self.b * scalar,
            self.a * scalar)

    def __neg__(self):
        return self * -1

    def __repr__(self):
        return "Colour(%s, %s, %s, %s)" % (self.r, self.g, self.b, self.a)

    def as_list(self):
        return [self.r, self.g, self.b, self.a]


class ImageBuffer:
    def __init__(self, image, sculpty=True, clear=True):
        self.sculpty = sculpty
        self.image = image
        self.x, self.y = self.image.size
        if clear:
            self.clear()
        else:
            self.buffer = list(self.image.pixels)

    def update(self):
        self.image.pixels = self.buffer

    def _buffer_pos(self, x, y):
        if x < 0 or y < 0 or x >= self.x or y >= self.y:
            return None
        return (x + y * self.x) * 4

    def _index(self, x, y):
        if self.sculpty:
            # skip true last pixels and wrap
            # u = 1.0 and v = 1.0 back to last pixels
            if x == self.x - 1:
                return None
            if y == self.y - 1:
                return None
            if x == self.x:
                x = x - 1
            if y == self.y:
                y = y - 1
        return self._buffer_pos(x, y)

    def clear(self):
        self.buffer = [0.0 for i in range(self.x * self.y * 4)]

    def clear_alpha(self, value=0.0):
        self.buffer[3::4] = [value for i in range(self.x * self.y)]

    def set_pixel(self, x, y, colour):
        index = self._index(x, y)
        if index is not None:
            self.buffer[index:index + 4] = colour.as_list()

    def get_pixel(self, x, y):
        index = self._index(x, y)
        if index is not None:
            return Colour(colour=self.buffer[index:index + 4])
        else:
            return None

    def colour_range(self):
        r_min = min(self.buffer[0::4])
        r_max = max(self.buffer[0::4])
        g_min = min(self.buffer[1::4])
        g_max = max(self.buffer[1::4])
        b_min = min(self.buffer[2::4])
        b_max = max(self.buffer[2::4])
        return (r_min, r_max, g_min, g_max, b_min, b_max)

    def set_buffer(self, x, y, colour):
        index = self._buffer_pos(x, y)
        if index is not None:
            self.buffer[index:index + 4] = colour.as_list()

    def get_buffer(self, x, y):
        index = self._buffer_pos(x, y)
        if index is not None:
            return Colour(colour=self.buffer[index:index + 4])
        else:
            return None

    def uv_to_xy(self, u, v):
        x = u * self.x
        if x % 1 > 0.5:
            x = ceil(x)
        else:
            x = int(x)
        y = v * self.y
        if y % 1 > 0.5:
            y = ceil(y)
        else:
            y = int(y)
        return x, y

    def get_vector(self, u, v):
        x, y = self.uv_to_xy(u, v)
        c = self.get_pixel(x, y)
        if c is None:
            # don't skip x-1 or y-1
            c = self.get_buffer(x, y)
        if c is not None:
            return (c.r - 0.5, c.g - 0.5, c.b - 0.5)
        return None

    def render_lod(self):
        self.sculpty = True
        for u in range(self.x + self.sculpty):
            for v in range(self.y + self.sculpty):
                c = Colour(float(u) / self.x, float(v) / self.y, 0.0)
                self.set_pixel(u, v, c)
        for lod in range(4):
            sides = [6, 8, 16, 32][lod]
            s, t = face_count(self.x, self.y, sides, sides, False)
            ss = [int(self.x * k / float(s)) for k in range(s)]
            ss.append(self.x)
            ts = [int(self.y * k / float(t)) for k in range(t)]
            ts.append(self.y)
            for s in ss:
                for t in ts:
                    c = self.get_pixel(s, t)
                    if c.b < 0.75:
                        c.b += 0.25
                    else:
                        c.b = 1.0
                    self.set_pixel(s, t, c)

    def draw_line(self, u1, v1, c1, u2, v2, c2, ends=True, alpha=False):
        '''Draws a gradient line'''
        if type(u1) == int:
            x1, y1, x2, y2 = u1, v1, u2, v2
        else:
            x1, y1 = self.uv_to_xy(u1, v1)
            x2, y2 = self.uv_to_xy(u2, v2)
        steep = abs(y2 - y1) > abs(x2 - x1)
        if steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            c1, c2 = c2, c1
        deltax = x2 - x1
        deltay = abs(y2 - y1)
        error = deltax / 2
        mix = c2 - c1
        y = y1
        if y1 < y2:
            ystep = 1
        else:
            ystep = -1
        for x in range(x1, x2 + 1):
            draw = ends or (x != x1 and x != x2)
            if not draw:
                #make sure we can skip this pixel
                if steep:
                    u, v = y, x
                else:
                    u, v = x, y
                c = self.get_pixel(u, v)
                if c is not None:
                    if c.a == 0:
                        draw = True
            if draw:
                d = x - x1
                if d:
                    if d == deltax:
                        colour = c2 * 1.0  # makes sure we are using copy
                    else:
                        colour = c1 + mix * (d / deltax)
                else:
                    colour = c1 * 1.0  # makes sure we are using copy
                if steep:
                    if alpha:
                        c = self.get_pixel(y, x)
                        if c is not None:
                            if c.a < colour.a:
                                c.a = colour.a
                                self.set_pixel(y, x, c)
                    else:
                        self.set_pixel(y, x, colour)
                else:
                    if alpha:
                        c = self.get_pixel(x, y)
                        if c is not None:
                            if c.a < colour.a:
                                c.a = colour.a
                                self.set_pixel(x, y, c)
                    else:
                        self.set_pixel(x, y, colour)
            error = error - deltay
            if error < 0:
                y = y + ystep
                error = error + deltax

    def get_first_x(self, y):
        for x in range(self.x + self.sculpty):
            c = self.get_pixel(x, y)
            if c is not None:
                if sum(c.as_list()) != 0:
                    return x, c
        return None, None

    def get_first_y(self, x):
        for y in range(self.y + self.sculpty):
            c = self.get_pixel(x, y)
            if c is not None:
                if sum(c.as_list()) != 0:
                    return y, c
        return None, None

    def fill_x(self):
        skip = False
        fill = False
        for v in range(self.y + self.sculpty):
            x, c = self.get_first_x(v)
            if x is None:
                skip = True
                continue
            elif x > 0:
                fill = True
            start_col = c
            start = 0
            for u in range(1, self.x + self.sculpty):
                new_col = self.get_pixel(u, v)
                if new_col == None:
                    continue
                if sum(new_col.as_list()) == 0:
                    if not fill:
                        fill = True
                else:
                    if fill:
                        fill = False
                        self.draw_line(start, v, start_col, u, v, new_col)
                    start = u
                    start_col = new_col
            if fill:
                fill = False
                self.draw_line(start, v, start_col, u, v, start_col)
        return skip

    def fill_y(self):
        skip = False
        fill = False
        for u in range(self.x + self.sculpty):
            y, c = self.get_first_y(u)
            if y is None:
                skip = True
                continue
            elif y > 0:
                fill = True
            start_col = c
            start = 0
            for v in range(1, self.y + self.sculpty):
                new_col = self.get_pixel(u, v)
                if new_col == None:
                    continue
                if sum(new_col.as_list()) == 0:
                    if not fill:
                        fill = True
                else:
                    if fill:
                        fill = False
                        self.draw_line(u, start, start_col, u, v, new_col)
                    start = v
                    start_col = new_col
            if fill:
                fill = False
                self.draw_line(u, start, start_col, u, v, start_col)
        return skip

    def fill(self):
        skip_x = self.fill_x()
        skip_y = self.fill_y()
        if skip_x:
            self.fill_x()

    def finalise(self):
        u_pixels, v_pixels = map_pixels(self.x, self.y)
        u_pixels.append(self.x)
        v_pixels.append(self.y)
        for u in u_pixels:
            for v in v_pixels:
                c = self.get_buffer(u, v)
                if c is None:
                    continue
                if sum(c.as_list()) == 0:
                    continue
                if u and u - 1 not in u_pixels:
                    self.set_buffer(u - 1, v, c)
                    if v and v - 1 not in v_pixels:
                        self.set_buffer(u - 1, v - 1, c)
                if v and v - 1 not in v_pixels:
                    self.set_buffer(u, v - 1, c)

    def alpha3d(self, u, v):
        c = self.get_buffer(u, v)
        f = (c.g * 0.35) + 0.65
        s = int((self.x - 1) * (0.5 - (0.5 - c.r) * f))
        t = int((self.y - 1) * (0.5 - (0.5 - c.b) * f))
        return s, t, c.g

    def render_preview(self):
        self.clear_alpha()
        ss, ts = map_pixels(self.x, self.y)
        for t in ts:
            s1, t1, a1 = self.alpha3d(ss[0], t)
            for s in ss[1:]:
                s2, t2, a2 = self.alpha3d(s, t)
                self.draw_line(s1, t1, Colour(0, 0, 0, a1),
                    s2, t2, Colour(0, 0, 0, a2), alpha=True)
                s1, t1, a1 = s2, t2, a2
        for s in ss:
            s1, t1, a1 = self.alpha3d(s, ts[0])
            for t in ts[1:]:
                s2, t2, a2 = self.alpha3d(s, t)
                self.draw_line(s1, t1, Colour(0, 0, 0, a1),
                    s2, t2, Colour(0, 0, 0, a2), alpha=True)
                s1, t1, a1 = s2, t2, a2

    def map_type(self):
        '''Returns the sculpt type of the sculpt map image'''
        poles = True
        xseam = True
        yseam = True
        u_pixels, v_pixels = map_pixels(self.x, self.y)
        p1 = self.buffer[0:3]
        i = self.x * (self.y - 1) * 4
        p2 = self.buffer[i:i + 3]
        if p1 != p2:
            yseam = False
        for u in u_pixels[1:]:
            i = u * 4
            p3 = self.buffer[i:i + 3]
            i = (u + self.x * (self.y - 1)) * 4
            p4 = self.buffer[i:i + 3]
            if p1 != p3 or p2 != p4:
                poles = False
            if p3 != p4:
                yseam = False
            p1 = p3
            p2 = p4
        for v in v_pixels:
            i = self.x * v * 4
            p1 = self.buffer[i:i + 3]
            i = i + (self.x - 1) * 4
            p2 = self.buffer[i:i + 3]
            if p1 != p2:
                xseam = False
        if xseam:
            if poles:
                return "SPHERE"
            if yseam:
                return "TORUS"
            return "CYLINDER"
        return "PLANE"

    def model(self):
        x, y = face_count(self.x, self.y, 32, 32)
        levels = 0
        while levels < 2 and x >= 8 and y >= 8 \
            and not ((x & 1) or (y & 1)):
            x = x >> 1
            y = y >> 1
            levels += 1
        return x, y, levels

    def add_as_object(self):
        faces_u, faces_v = face_count(self.x, self.y, 32, 32)
        map_type = self.map_type()
        wrap_v = map_type == "TORUS"
        wrap_u = map_type != "PLANE"
        verts_u = faces_u + 1
        verts_v = faces_v + 1
        if wrap_u and faces_u == 1:
            verts_u += 1
        if wrap_v and faces_v == 1:
            verts_v += 1
        actual_u = verts_u - wrap_u
        actual_v = verts_v - wrap_v
        uvgrid_u = []
        uvgrid_v = []
        uvgrid_s = []
        uvgrid_t = []
        s, t, w, h, clean_s, clean_t = map_size(
            verts_u - 1, verts_v - 1, 0)
        level_mask = 0xFFFE
        # uvgrid_s and uvgrid_t will hold uv layout positions
        for i in range(s):
            p = w * i / float(s)
            if clean_s:
                p = int(p) & level_mask
            if p:
                p = p / float(w)
            uvgrid_s.append(p)
        uvgrid_s.append(1.0)
        for i in range(t):
            p = h * i / float(t)
            if clean_t:
                p = int(p) & level_mask
            if p:
                p = p / float(h)
            uvgrid_t.append(p)
        uvgrid_t.append(1.0)

        # build list of 3D locations for vertices
        verts = []
        for v in range(actual_v):
            for u in range(actual_u):
                vec_u = u / (verts_u - 1)
                vec_v = v / (verts_v - 1)
                verts.append(self.get_vector(vec_u, vec_v))

        # build list of faces
        faces = []
        first_row = range(actual_u)
        for v in range(1, actual_v):
            second_row = [idx + actual_u for idx in first_row]
            faces.extend(createFaces(first_row, second_row, wrap_u))
            first_row = second_row
        if wrap_v:
            faces.extend(createFaces(second_row, range(actual_u), wrap_u))

        # build list of seams - these should be all edges with
        # u=0 and/or with v=0 depending on wrap settings
        seams = []
        if wrap_u:
            first_vertex = 0
            for i in range(actual_v - 1):
                second_vertex = first_vertex + actual_u
                seams.append((first_vertex, second_vertex))
                first_vertex = second_vertex
            if wrap_v:
                seams.append((0, first_vertex))
        if wrap_v:
            first_vertex = 0
            for i in range(actual_u - 1):
                second_vertex = first_vertex + 1
                seams.append((first_vertex, second_vertex))
                first_vertex = second_vertex
            if wrap_u:
                seams.append((0, first_vertex))

        context = bpy.context
        create_mesh_object(context, verts, [], faces, self.image.name)
        obj = context.active_object
        # end up in edit mode here if set in preferences, so set back.
        bpy.ops.object.mode_set(mode='OBJECT')
        markSeams(obj.data, seams)

        # build list of uv faces
        uvfaces = []
        first_row = [(uvgrid_s[u], 0.0) for u in range(verts_u)]
        for v in range(1, verts_v):
            second_row = [(uvgrid_s[u], uvgrid_t[v]) for u in range(verts_u)]
            faces = createFaces(first_row, second_row, False)
            if wrap_u:
                # match face order of wrapped mesh
                faces = [faces[-1]] + faces[:-1]
                # correct vert order for wrapped face
                fix = faces[0]
                faces[0] = (fix[2], fix[3], fix[0], fix[1])
            uvfaces.extend(faces)
            first_row = second_row

        # create UVTex layout
        uvtex = obj.data.uv_textures.new()
        for face_idx in range(len(uvfaces)):
            uvtex.data[face_idx].uv1 = uvfaces[face_idx][0]
            uvtex.data[face_idx].uv2 = uvfaces[face_idx][1]
            uvtex.data[face_idx].uv3 = uvfaces[face_idx][2]
            uvtex.data[face_idx].uv4 = uvfaces[face_idx][3]

        s_map = uvtex
        s_map.name = "sculptie"
        for f in s_map.data:
            f.image = self.image
            f.use_image = True
        obj.prim.type = 'PRIM_TYPE_SCULPT'
        obj.prim.sculpt_type = "PRIM_SCULPT_TYPE_%s" % map_type

        bpy.ops.object.mode_set(mode='EDIT')

        # blender bug: inside not working when set to self.flip_normals
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.faces_shade_smooth()

        if not context.user_preferences.edit.use_enter_edit_mode:
            bpy.ops.object.mode_set(mode='OBJECT')

        if 'vmin' in self.image:
            vmin = self.image['vmin']
            vmax = self.image['vmax']
            vscale = self.image['vscale']
            sx = vmax[0] - vmin[0]
            sy = vmax[1] - vmin[1]
            sz = vmax[2] - vmin[2]
            obj.scale = (sx * vscale[0], sy * vscale[1], sz * vscale[2])


def edge_draw_list(mesh):
    face_idx = len(mesh.faces) - 1
    edge_idx = len(mesh.faces[face_idx].edge_keys)
    while edge_idx > 0 or face_idx > 0:
        if edge_idx == 0:
            face_idx -= 1
            edge_idx = len(mesh.faces[face_idx].edge_keys)
        edge_idx -= 1
        edge = mesh.faces[face_idx].edge_keys[edge_idx]
        vert1 = mesh.vertices[edge[0]].co
        vert2 = mesh.vertices[edge[1]].co
        ends = not edge_idx % 2
        uv = mesh.uv_textures['sculptie'].data[face_idx].uv_raw
        verts = [v for v in mesh.faces[face_idx].vertices]
        v1_idx = verts.index(edge[0])
        v2_idx = verts.index(edge[1])
        uv_idx = 2 * v1_idx
        u1, v1 = uv[uv_idx:uv_idx + 2]
        uv_idx = 2 * v2_idx
        u2, v2 = uv[uv_idx:uv_idx + 2]
        yield (u1, v1, vert1, u2, v2, vert2, ends)


def bounding_box(mesh):
    v0 = mesh.vertices[0].co
    vmin = Vector((v0.x, v0.y, v0.z))
    vmax = Vector((v0.x, v0.y, v0.z))
    for i in range(1, len(mesh.vertices)):
        v = mesh.vertices[i].co
        vmin.x = min(vmin.x, v.x)
        vmin.y = min(vmin.y, v.y)
        vmin.z = min(vmin.z, v.z)
        vmax.x = max(vmax.x, v.x)
        vmax.y = max(vmax.y, v.y)
        vmax.z = max(vmax.z, v.z)
    return vmin, vmax


def bake(object, scene, vmin=None, vmax=None, rename=False):
    try:
        is_editmode = (bpy.context.active_object.mode == 'EDIT')
    except:
        is_editmode = False
    if is_editmode:
        bpy.ops.object.mode_set(mode='OBJECT')
    if not is_active(object):
        return False

    img = object.data.uv_textures['sculptie'].data[0].image
    if not img.has_data:
        img.source = 'GENERATED'
    buffer = ImageBuffer(img)
    mesh = object.to_mesh(scene, True, 'RENDER')
    if vmin is None:
        vmin, vmax = bounding_box(mesh)
    sx = (vmax.x - vmin.x)
    sy = (vmax.y - vmin.y)
    sz = (vmax.z - vmin.z)
    if sx == 0:
        sx = 1.0
        vmax.x += 0.5
        vmin.x -= 0.5
    if sy == 0:
        sy = 1.0
        vmax.y += 0.5
        vmin.y -= 0.5
    if sz == 0:
        sz = 1.0
        vmax.z += 0.5
        vmin.z -= 0.5
    if sx * object.scale.x < 0.01:
        n = 0.005 / object.scale.x
        m = vmin.x + 0.5 * sx
        vmin.x = m - n
        vmax.x = m + n
        sx = 2 * n
    if sy * object.scale.y < 0.01:
        n = 0.005 / object.scale.y
        m = vmin.y + 0.5 * sy
        vmin.y = m - n
        vmax.y = m + n
        sy = 2 * n
    if sz * object.scale.z < 0.01:
        n = 0.005 / object.scale.z
        m = vmin.z + 0.5 * sz
        vmin.z = m - n
        vmax.z = m + n
        sz = 2 * n
    sx = 1.0 / sx
    sy = 1.0 / sy
    sz = 1.0 / sz
    img['vmin'] = vmin
    img['vmax'] = vmax
    img['vscale'] = object.scale
    for u1, v1, vert1, u2, v2, vert2, ends in edge_draw_list(mesh):
        r = (vert1.x - vmin.x) * sx
        g = (vert1.y - vmin.y) * sy
        b = (vert1.z - vmin.z) * sz
        c1 = Colour(r, g, b)
        r = (vert2.x - vmin.x) * sx
        g = (vert2.y - vmin.y) * sy
        b = (vert2.z - vmin.z) * sz
        c2 = Colour(r, g, b)
        buffer.draw_line(u1, v1, c1, u2, v2, c2, ends)
    buffer.fill()
    if buffer.x * buffer.y <= 8192:
        buffer.finalise()
        buffer.render_preview()
    if rename:
        buffer.image.name = object.name
    buffer.update()
    bpy.data.meshes.remove(mesh)

    if is_editmode:
        bpy.ops.object.mode_set(mode='EDIT')

    return True


def sculpt_type(obj):
    def about(v1, v2):
        p = 0.002
        v3 = v1 - v2
        for v in v3:
            if -p > v or p < v:
                return False
        return True
    top = []
    bottom = []
    left = []
    right = []
    for u1, v1, vert1, u2, v2, vert2, ends in edge_draw_list(obj.data):
        if v1 == 0 and v2 == 0:
            bottom.append(vert1)
            bottom.append(vert2)
        if v1 == 1.0 and v2 == 1.0:
            top.append(vert1)
            top.append(vert2)
        if u1 == 0 and u2 == 0:
            left.append(vert1)
            left.append(vert2)
        if u1 == 1.0 and u2 == 1.0:
            right.append(vert1)
            right.append(vert2)
    top.sort()
    bottom.sort()
    left.sort()
    right.sort()
    if top == bottom:
        wrap_v = True
    else:
        wrap_v = False
    if left == right:
        wrap_u = True
    else:
        wrap_u = False
    if wrap_v and not wrap_u:
        # correct rotation
        for f in obj.data.uv_textures['sculptie'].data:
            uv = []
            for u, v in f.uv:
                uv.append(1.0 - v)
                uv.append(1.0 - u)
            f.uv_raw = uv
        wrap_u, wrap_v = wrap_v, wrap_u
        top, right, bottom, left = left, top, right, bottom
    if wrap_u:
        if wrap_v:
            sculpt_type = "TORUS"
        elif about(min(bottom), max(bottom)) and about(min(top), max(top)):
            sculpt_type = "SPHERE"
        else:
            sculpt_type = "CYLINDER"
    else:
        sculpt_type = "PLANE"
    return sculpt_type


def get_vector(image_buffer, u, v):
    x = int(u * self.buffer.x)
    y = int(v * self.buffer.y)
    c = self.buffer.get_pixel(x, y)
    if c is not None:
        return (c.r - 0.5, c.g - 0.5, c.b - 0.5)
    return None


def update_from_image(object, image):
    buffer = ImageBuffer(image, clear=False)
    mesh = object.data
    face_idx = len(mesh.faces) - 1
    edge_idx = len(mesh.faces[face_idx].edge_keys)
    while edge_idx > 0 or face_idx > 0:
        if edge_idx == 0:
            face_idx -= 1
            edge_idx = len(mesh.faces[face_idx].edge_keys)
        edge_idx -= 1
        if not edge_idx % 2:
            edge = mesh.faces[face_idx].edge_keys[edge_idx]
            vert1 = mesh.vertices[edge[0]]
            vert2 = mesh.vertices[edge[1]]
            uv = mesh.uv_textures['sculptie'].data[face_idx].uv_raw
            verts = [v for v in mesh.faces[face_idx].vertices]
            v1_idx = verts.index(edge[0])
            v2_idx = verts.index(edge[1])
            uv_idx = 2 * v1_idx
            u1, v1 = uv[uv_idx:uv_idx + 2]
            uv_idx = 2 * v2_idx
            u2, v2 = uv[uv_idx:uv_idx + 2]
            c = buffer.get_vector(u1, v1)
            if c is not None and vert1.select:
                vert1.co = c
            c = buffer.get_vector(u2, v2)
            if c is not None and vert2.select:
                vert2.co = c
    mesh.update()
