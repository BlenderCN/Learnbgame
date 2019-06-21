#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

import bgl
import blf
import mathutils
from mathutils import Color, Vector, Matrix, Quaternion, Euler

import math

from .utils_math import clamp_angle

#============================================================================#

# TODO: update to match the current API!
# TODO: implement all the OpenGL features (+other conveniences)
# TODO: documentation

'''
Speed tips:
* Static methods are faster than instance/class methods
  Seems like argument passing is a relatively expensive operation
* Closure dictionary lookup with constant key is faster:
    # non-arguments are assumed to be closure-bound objects
    def f(enum): g(enum)
    f(GL_BLEND) # bgl.GL_BLEND is even slower
    def f(enum): g(enums[enum])
    f('BLEND') # faster
'''

# Convention:
# UPPER_CASE is for enabled/disabled capabilities and constants
# CamelCase is for parameters/functions
# lower_case is for extra functionality

# Alternative:
# NAME/Name for set
# NAME_/Name_ for get
# or: get_Name, set_Name to not conflict with properties

class StateRestorator:
    def __init__(self, obj, args, kwargs):
        _previous = {}
        for k in args:
            _previous[k] = getattr(obj, k)
        for k, v in kwargs.items():
            _previous[k] = getattr(obj, k)
            setattr(obj, k, v)
        self._previous = _previous
        self._obj = obj
    
    def restore(self):
        obj = self._obj
        for k, v in self._previous.items():
            setattr(obj, k, v)
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.restore()

def make_RenderBatch():
    # implementations:
    # None (same as mode, or compatible), LINES, TRIANGLES
    # also: VBO? DISPLAY_LIST?
    _gl_modes = {
        'POINTS':bgl.GL_POINTS,
        'LINES':bgl.GL_LINES,
        'LINE_STRIP':bgl.GL_LINE_STRIP,
        'LINE_LOOP':bgl.GL_LINE_LOOP,
        'TRIANGLES':bgl.GL_TRIANGLES,
        'TRIANGLE_STRIP':bgl.GL_TRIANGLE_STRIP,
        'TRIANGLE_FAN':bgl.GL_TRIANGLE_FAN,
        'QUADS':bgl.GL_QUADS,
        'QUAD_STRIP':bgl.GL_QUAD_STRIP,
        'POLYGON':bgl.GL_POLYGON,
        # CONVEX ?
    }
    _begin = bgl.glBegin
    _end = bgl.glEnd
    _vertex = bgl.glVertex4d
    
    class RenderBatch:
        def __init__(self, mode, implementation=None):
            self.mode = _gl_modes[mode]
        
        def begin(self):
            _begin(self.mode)
        
        def end(self):
            _end()
        
        def __enter__(self):
            self.begin()
            return self
        
        def __exit__(self, type, value, traceback):
            self.end()
        
        def vertex(self, x, y, z=0.0, w=1.0):
            _vertex(x, y, z, w)
        
        def sequence(self, seq):
            for v in seq:
                self.vertex(*v)
        
        @classmethod
        def arc(cls, center, extents, resolution=2.0, start=0.0, end=2.0*math.pi, skip_start=0, skip_end=0):
            sin = math.sin
            cos = math.cos
            
            x0 = center[0]
            y0 = center[1]
            if isinstance(extents, (int, float)):
                xs = extents
                ys = extents
            else:
                xs = extents[0]
                ys = extents[1]
            
            sector = end - start
            n = resolution
            if isinstance(n, float): n = int(round((abs(sector) * max(xs, ys)) / n))
            n = max(n, 2)
            step = sector / n
            for i in range(skip_start, n - skip_end + 1):
                angle = start + step * i
                yield (x0 + sin(angle) * xs, y0 + cos(angle) * ys)
        
        circle = arc
        oval = arc
        
        @classmethod
        def rounded_primitive(cls, verts, radius, resolution=2.0):
            if not verts: return
            if len(verts) == 1:
                yield from cls.arc(verts[0], radius, resolution, skip_end=1)
            elif len(verts) == 2:
                v0, v1 = verts
                dv = v1 - v0
                angle = Vector((0,1)).angle_signed(Vector((-dv.y, dv.x)), 0.0)
                yield from cls.arc(v0, radius, resolution, angle-math.pi, angle)
                yield from cls.arc(v1, radius, resolution, angle, angle+math.pi)
            elif radius == 0:
                yield from verts # exactly the same
            else:
                vref = Vector((0,1))
                count = len(verts)
                for i0 in range(count):
                    v0 = verts[i0]
                    v1 = verts[(i0 + 1) % count]
                    v2 = verts[(i0 + 2) % count]
                    dv10 = v1 - v0
                    dv21 = v2 - v1
                    angle10 = vref.angle_signed(Vector((-dv10.y, dv10.x)), 0.0)
                    angle21 = vref.angle_signed(Vector((-dv21.y, dv21.x)), 0.0)
                    angle21 = angle10 + clamp_angle(angle21 - angle10)
                    yield from cls.arc(v1, radius, resolution, angle10, angle21)
    
    return RenderBatch

RenderBatch = make_RenderBatch()
del make_RenderBatch

class CGL:
    Matrix_ModelView_2D = None
    Matrix_Projection_2D = None
    Matrix_ModelView_3D = None
    Matrix_Projection_3D = None
    
    def __call__(self, *args, **kwargs):
        return StateRestorator(self, args, kwargs)
    
    def batch(self, mode):
        return RenderBatch(mode)
    
    @staticmethod
    def read_zbuffer(xy, wh=(1, 1), centered=False, src=None):
        if isinstance(wh, (int, float)):
            wh = (wh, wh)
        elif len(wh) < 2:
            wh = (wh[0], wh[0])
        
        x, y, w, h = int(xy[0]), int(xy[1]), int(wh[0]), int(wh[1])
        
        if centered:
            x -= w // 2
            y -= h // 2
        
        buf_size = w*h
        
        if src is None:
            # xy is in window coordinates!
            zbuf = bgl.Buffer(bgl.GL_FLOAT, [buf_size])
            bgl.glReadPixels(x, y, w, h, bgl.GL_DEPTH_COMPONENT, bgl.GL_FLOAT, zbuf)
        else:
            src, w0, h0 = src
            template = [0.0] * buf_size
            for dy in range(h):
                y0 = min(max(y + dy, 0), h0-1)
                for dx in range(w):
                    x0 = min(max(x + dx, 0), w0-1)
                    i0 = x0 + y0 * w0
                    i1 = dx + dy * w
                    template[i1] = src[i0]
            zbuf = bgl.Buffer(bgl.GL_FLOAT, [buf_size], template)
        
        return zbuf
    
    @staticmethod
    def polygon_stipple_from_list(L, zeros=False, tile=True):
        if isinstance(L, str):
            L = L.strip("\n").split("\n")
            if not isinstance(zeros, str): zeros = " "
        
        L_rows = len(L)
        if L_rows == 0:
            return [[0]*4]*32
        
        rows = []
        for i in range(32):
            if i >= L_rows:
                if tile:
                    rows.append(rows[i % L_rows])
                else:
                    rows.append([0, 0, 0, 0])
                continue
            
            L_col = L[i]
            L_cols = len(L_col)
            
            cols = [0, 0, 0, 0]
            j = 0
            for col in range(4):
                for shift in range(8):
                    if j >= L_cols:
                        if tile:
                            value = L_col[j % L_cols]
                        else:
                            value = zeros
                    else:
                        value = L_col[j]
                    
                    if value != zeros:
                        cols[col] |= 1 << (7 - shift)
                        #cols[col] |= 1 << shift
                    j += 1
            
            rows.append(cols)
        
        return list(reversed(rows))
        #return rows
    
    def CallList(self, id):
        pass

# Quick & dirty hack to have same object throughout the script reloads
if "cgl" not in locals(): cgl = CGL()

def fill_BLF():
    options = {'CLIPPING':blf.CLIPPING, 'KERNING_DEFAULT':blf.KERNING_DEFAULT, 'ROTATION':blf.ROTATION, 'SHADOW':blf.SHADOW}
    
    blf_load = blf.load
    blf_unload = blf.unload
    blf_enable = blf.enable
    blf_disable = blf.disable
    blf_shadow = blf.shadow
    blf_shadow_offset = blf.shadow_offset
    blf_blur = blf.blur
    blf_position = blf.position
    blf_rotation = blf.rotation
    blf_size = blf.size
    blf_clipping = blf.clipping
    blf_aspect = blf.aspect
    blf_dimensions = blf.dimensions
    blf_draw = blf.draw
    
    class BatchedText:
        def __init__(self, font, pieces, size):
            self.font = font
            self.pieces = pieces
            self.size = size
        
        def draw(self, pos, origin=None, text=None, background=None, outline=None, radius=0, resolution=2.0):
            font = self.font
            
            x = pos[0]
            y = pos[1]
            z = (pos[2] if len(pos) > 2 else 0)
            
            if origin:
                x -= self.size[0] * origin[0]
                y -= self.size[1] * origin[1]
            
            if background or outline:
                v0 = Vector((x, y, z))
                dx = Vector((self.size[0], 0, 0))
                dy = Vector((0, self.size[1], 0))
                verts = (v0, v0+dy, v0+dx+dy, v0+dx)
                verts = tuple(RenderBatch.rounded_primitive(verts, radius, resolution))
            
            cgl.BLEND = True
            
            if background:
                if len(background) == 3:
                    cgl.Color3 = background
                else:
                    cgl.Color = background
                with cgl.batch('POLYGON') as batch:
                    batch.sequence(verts)
            
            if outline:
                if len(outline) == 3:
                    cgl.Color3 = outline
                else:
                    cgl.Color = outline
                with cgl.batch('LINE_LOOP') as batch:
                    batch.sequence(verts)
            
            if text:
                if len(text) == 3:
                    cgl.Color3 = text
                else:
                    cgl.Color = text
            
            if text or (not (background or outline)):
                x0, y0 = round(x), round(y)
                for txt, x, y in self.pieces:
                    blf_position(font, x0+x, y0+y, z)
                    blf_draw(font, txt)
    
    class Text:
        font = 0 # 0 is the default font
        
        # load / unload
        def load(self, filename, size=None, dpi=72):
            font = blf_load(filename)
            if size is not None: blf_size(font, size, dpi)
            return font
        def unload(self, filename):
            blf_unload(filename)
        
        # enable / disable options
        def enable(self, option):
            blf_enable(self.font, options[option])
        def disable(self, option):
            blf_disable(self.font, options[option])
        
        # set effects (shadow, blur)
        def shadow(self, level, r, g, b, a):
            blf_shadow(self.font, level, r, g, b, a)
        def shadow_offset(self, x, y):
            blf_shadow_offset(self.font, x, y)
        def blur(self, radius):
            blf_blur(self.font, radius)
        
        # set position / rotation / size
        def position(self, x, y, z=0.0):
            blf_position(self.font, x, y, z)
        def rotation(self, angle):
            blf_rotation(self.font, angle)
        def size(self, size, dpi=72):
            blf_size(self.font, size, dpi)
        
        # set clipping / aspect
        def clipping(self, xmin, ymin, xmax, ymax):
            blf_clipping(self.font, xmin, ymin, xmax, ymax)
        def aspect(self, aspect):
            blf_aspect(self.font, aspect)
        
        def compile(self, text, width=None, alignment=None):
            font = self.font
            
            if width is None:
                lines, size = [text], blf_dimensions(font, text)
            else:
                lines, size = self.wrap_text(text, width, font=font)
            
            if (alignment in (None, 'LEFT')): alignment = 0.0
            elif (alignment == 'CENTER'): alignment = 0.5
            elif (alignment == 'RIGHT'): alignment = 1.0
            
            pieces = []
            x, y = 0, 0
            w, h = size
            for line in lines:
                line_size = blf_dimensions(font, line)
                x = (w - line_size[0]) * alignment
                pieces.append((line, round(x), round(y)))
                y += line_size[1]
            
            return BatchedText(font, pieces, size)
        
        # drawing (WARNING: modifies BLEND state)
        def draw(self, text, pos=None, origin=None, width=None, alignment=None):
            font = self.font
            
            if pos is None: # if position not specified, other calculations cannot be performed
                blf_draw(font, text)
            elif width is not None: # wrap+align
                lines, size = self.wrap_text(text, width, font=font)
                
                x = pos[0]
                y = pos[1]
                z = (pos[2] if len(pos) > 2 else 0)
                
                if origin:
                    x -= size[0] * origin[0]
                    y -= size[1] * origin[1]
                
                if (alignment in (None, 'LEFT')): alignment = 0.0
                elif (alignment == 'CENTER'): alignment = 0.5
                elif (alignment == 'RIGHT'): alignment = 1.0
                
                x0, y0 = x, y
                w, h = size
                for line in lines:
                    line_size = blf_dimensions(font, line)
                    x = x0 + (w - line_size[0]) * alignment
                    blf_position(font, round(x), round(y), z)
                    blf_draw(font, line)
                    y += line_size[1]
            else:
                x = pos[0]
                y = pos[1]
                z = (pos[2] if len(pos) > 2 else 0)
                
                if origin:
                    size = blf_dimensions(font, text)
                    x -= size[0] * origin[0]
                    y -= size[1] * origin[1]
                
                blf_position(font, round(x), round(y), z)
                blf_draw(font, text)
        
        # dimensions & wrapping calculation
        def dimensions(self, text, font=None):
            if font is None: font = self.font
            return blf_dimensions(font, text)
        
        def _split_word(self, width, x, max_x, word, lines, font):
            line = ""
            
            for c in word:
                x_dx = x + blf_dimensions(font, line+c)[0]
                
                if (x_dx) > width:
                    x_dx = blf_dimensions(font, line)[0]
                    lines.append(line)
                    line = c
                    x = 0
                else:
                    line += c
                
                max_x = max(x_dx, max_x)
            
            return line, x, max_x

        def _split_line(self, width, x, max_x, line, lines, font):
            words = line.split(" ")
            line = ""
            
            for word in words:
                c = (word if not line else " " + word)
                x_dx = x + blf_dimensions(font, line+c)[0]
                
                if (x_dx) > width:
                    x_dx = blf_dimensions(font, line)[0]
                    if not line:
                        # one word is longer than the width
                        line, x, max_x = self._split_word(width, x, max_x, word, lines, font)
                    else:
                        lines.append(line)
                        line = word
                    x = 0
                else:
                    line += c
                
                max_x = max(x_dx, max_x)
            
            if line: lines.append(line)
            
            return max_x

        def split_text(self, width, x, max_x, text, lines, font=None):
            if font is None: font = self.font
            
            for line in text.splitlines():
                if not line:
                    lines.append("")
                else:
                    max_x = self._split_line(width, x, max_x, line, lines, font)
                x = 0
            
            return max_x

        def wrap_text(self, text, width, indent=0, font=None):
            """
            Splits text into lines that don't exceed the given width.
            text -- the text.
            width -- the width the text should fit into.
            font -- the id of the typeface as returned by blf.load(). Defaults to 0 (the default font).
            indent -- the indent of the paragraphs. Defaults to 0.
            Returns: lines, actual_width
            lines -- the list of the resulting lines
            actual_width -- the max width of these lines (may be less than the supplied width).
            """
            
            if font is None: font = self.font
            
            line_height = blf_dimensions(font, "!")[1]
            
            lines = []
            max_x = 0
            for line in text.splitlines():
                if not line:
                    lines.append("")
                else:
                    max_x = self._split_line(width, indent, max_x, line, lines, font)
            
            return lines, (max_x, len(lines)*line_height)
    
    cgl.text = Text()

fill_BLF()
del fill_BLF

def fill_CGL():
    def Cap(name, doc=""):
        pname = name[3:]
        if hasattr(CGL, pname):
            return
        
        is_enabled = bgl.glIsEnabled
        enabler = bgl.glEnable
        disabler = bgl.glDisable
        
        state_id = getattr(bgl, name)
        
        class Descriptor:
            __doc__ = doc
            def __get__(self, instance, owner):
                return is_enabled(state_id)
            def __set__(self, instance, value):
                (enabler if value else disabler)(state_id)
        
        setattr(CGL, pname, Descriptor())
    ###############################################################
    
    def State(name, doc, *params):
        pname = name[2:].split(":")[0] # e.g. "glColor:4fv" -> "Color"
        if hasattr(CGL, pname): return
        
        name = name.replace(":", "") # e.g. "glColor:4fv" -> "glColor4fv"
        
        localvars = {"doc":doc, "Buf":bgl.Buffer, "bool":bool, "int":int, "float":float}
        
        args_info = []
        for param in params:
            arg_type = param[0] # e.g. "float:4"
            arg_key = param[1] # e.g. GL_CURRENT_COLOR
            state_getter = (param[2] if len(param) > 2 else None) # when generic getter is not applicable
            
            getter_specific = "{0}"
            setter_specific = "{0}"
            
            arg_id = len(args_info)
            
            if isinstance(arg_type, set):
                data_type = bgl.GL_INT
                data_size = 1
                state_getter = state_getter or bgl.glGetIntegerv
                
                enum = {}
                enum_inv = {}
                for enum_item in arg_type:
                    enum_value = getattr(bgl, "GL_" + enum_item)
                    enum[enum_item] = enum_value
                    enum_inv[enum_value] = enum_item
                
                localvars["_enum%s" % arg_id] = enum
                localvars["_enum_inv%s" % arg_id] = enum_inv
                
                getter_specific = "_enum_inv%s[{0}]" % arg_id
                setter_specific = "_enum%s[{0}]" % arg_id
            elif arg_type.startswith("bool"):
                data_type = bgl.GL_INT
                data_size = eval(arg_type.split(":")[1])
                state_getter = state_getter or bgl.glGetIntegerv
                if data_size == 1:
                    getter_specific = "bool({0})"
                    setter_specific = "int({0})"
                else:
                    getter_specific = "[bool(b) for b in {0}]"
                    setter_specific = "[int(b) for b in {0}]"
            elif arg_type.startswith("byte"):
                data_type = bgl.GL_BYTE
                data_size = eval(arg_type.split(":")[1])
                state_getter = state_getter or bgl.glGetIntegerv
            elif arg_type.startswith("int"):
                data_type = bgl.GL_INT
                data_size = eval(arg_type.split(":")[1])
                state_getter = state_getter or bgl.glGetIntegerv
            elif arg_type.startswith("float"):
                data_type = bgl.GL_FLOAT
                data_size = eval(arg_type.split(":")[1])
                state_getter = state_getter or bgl.glGetFloatv
            else:
                data_type = None
                data_size = None
                state_getter = None
            
            if data_size == 1:
                getter_specific = getter_specific.format("{0}[0]")
                setter_specific = setter_specific.format("{0}")
            else:
                getter_specific = getter_specific.format("{0}.to_list()")
                setter_specific = setter_specific.format("Buf(_type%s, %s, {0})" % (arg_id, data_size))
            
            state_id = (None if arg_key is None else getattr(bgl, arg_key))
            buf = bgl.Buffer(data_type, data_size)
            
            localvars["_getter%s" % arg_id] = state_getter
            localvars["_state_id%s" % arg_id] = state_id
            localvars["_buf%s" % arg_id] = buf
            localvars["_type%s" % arg_id] = data_type
            
            args_info.append((getter_specific, setter_specific))
        
        getter_lines = []
        setter_lines = []
        return_args = []
        setter_args = []
        any_specific = False
        for i in range(len(args_info)):
            getter_specific, setter_specific = args_info[i]
            
            if localvars["_state_id%s" % i] is None:
                getter_lines.append("   _getter{0}(_buf{0})".format(i))
            else:
                getter_lines.append("   _getter{0}(_state_id{0}, _buf{0})".format(i))
            
            return_args.append(getter_specific.format("_buf%s" % i))
            
            if setter_specific != "{0}":
                any_specific = True
            setter_args.append(setter_specific.format("value[%s]" % i))
        
        if len(args_info) == 1:
            setter_args = [args_info[0][1].format("value")]
        elif not any_specific:
            setter_args = ["*value"]
        
        localvars["_setter"] = getattr(bgl, name)
        
        get_body = "{0}\n   return {1}".format("\n".join(getter_lines), ", ".join(return_args))
        set_body = "{0}\n   _setter({1})".format("\n".join(setter_lines), ", ".join(setter_args))
        
        code = """
def make(**kwargs):
 locals().update(kwargs)
 class Descriptor:
  __doc__ = doc
  def __get__(self, instance, owner):\n{0}
  def __set__(self, instance, value):\n{1}
 return Descriptor
""".format(get_body, set_body)
        #print(code)
        exec(code, localvars, localvars)
        
        Descriptor = localvars["make"](**localvars)
        
        setattr(CGL, pname, Descriptor())
    ###############################################################
    
    def add_descriptor(name, getter, setter, doc=""):
        Descriptor = type(name+"_Descriptor", (object,), {
            "__doc__":doc, "__get__":getter, "__set__":setter})
        setattr(CGL, name, Descriptor())
    
    Cap('GL_ALPHA_TEST')
    Cap('GL_AUTO_NORMAL')
    Cap('GL_BLEND')
    for i in range(6):
        Cap('GL_CLIP_PLANE%s' % i)
    #Cap('GL_COLOR_LOGIC_OP')
    Cap('GL_COLOR_MATERIAL')
    #Cap('GL_COLOR_TABLE')
    #Cap('GL_CONVOLUTION_1D')
    #Cap('GL_CONVOLUTION_2D')
    Cap('GL_CULL_FACE')
    Cap('GL_DEPTH_TEST')
    Cap('GL_DEPTH_WRITEMASK') # it's not a cap! see glDepthMask
    Cap('GL_DITHER')
    Cap('GL_FOG')
    #Cap('GL_HISTOGRAM')
    #Cap('GL_INDEX_LOGIC_OP')
    for i in range(8):
        Cap('GL_LIGHT%s' % i)
    Cap('GL_LIGHTING')
    Cap('GL_LINE_SMOOTH')
    Cap('GL_LINE_STIPPLE')
    for i in (1, 2):
        Cap('GL_MAP%s_COLOR_4' % i)
        Cap('GL_MAP%s_INDEX' % i)
        Cap('GL_MAP%s_NORMAL' % i)
        for j in (1, 2, 3, 4):
            Cap('GL_MAP%s_TEXTURE_COORD_%s' % (i, j))
        for j in (3, 4):
            Cap('GL_MAP%s_VERTEX_%s' % (i, j))
    #Cap('GL_MINMAX')
    Cap('GL_NORMALIZE')
    Cap('GL_POINT_SMOOTH')
    Cap('GL_POLYGON_OFFSET_FILL')
    Cap('GL_POLYGON_OFFSET_LINE')
    Cap('GL_POLYGON_OFFSET_POINT')
    Cap('GL_POLYGON_SMOOTH')
    Cap('GL_POLYGON_STIPPLE')
    #Cap('GL_POST_COLOR_MATRIX_COLOR_TABLE')
    #Cap('GL_POST_CONVOLUTION_COLOR_TABLE')
    #Cap('GL_RESCALE_NORMAL')
    #Cap('GL_SEPARABLE_2D')
    Cap('GL_SCISSOR_TEST')
    Cap('GL_STENCIL_TEST')
    # currently 3D texture cap not defined in bgl
    for i in (1, 2):#(1, 2, 3):
        Cap('GL_TEXTURE_%sD' % i)
    for c in "QRST":
        Cap('GL_TEXTURE_GEN_%s' % c)
    
    State('glLineWidth', "", ("int:1", 'GL_LINE_WIDTH'))
    State('glShadeModel', "", ({'FLAT', 'SMOOTH'}, 'GL_SHADE_MODEL'))
    State('glColor:4fv', "", ("float:4", 'GL_CURRENT_COLOR')) # GL_COLOR ?
    State('glColor3:fv', "", ("float:3", 'GL_CURRENT_COLOR')) # GL_COLOR ?
    State('glBlendFunc', "", # Somewhy CONST modes aren't present in bgl %)
        ({'ZERO', 'ONE', 'SRC_COLOR', 'ONE_MINUS_SRC_COLOR', 'DST_COLOR', 'ONE_MINUS_DST_COLOR', 'SRC_ALPHA', 'ONE_MINUS_SRC_ALPHA', 'DST_ALPHA', 'ONE_MINUS_DST_ALPHA', 'SRC_ALPHA_SATURATE'}, 'GL_BLEND_SRC'),
        ({'ZERO', 'ONE', 'SRC_COLOR', 'ONE_MINUS_SRC_COLOR', 'DST_COLOR', 'ONE_MINUS_DST_COLOR', 'SRC_ALPHA', 'ONE_MINUS_SRC_ALPHA', 'DST_ALPHA', 'ONE_MINUS_DST_ALPHA'}, 'GL_BLEND_DST'))
    # added 2015-01-02
    State('glDepthFunc', "", ({'NEVER', 'LESS', 'EQUAL', 'LEQUAL', 'GREATER', 'NOTEQUAL', 'GEQUAL', 'ALWAYS'}, 'GL_DEPTH_FUNC'))
    State('glLineStipple', "", ("int:1", 'GL_LINE_STIPPLE_REPEAT'), ("int:1", 'GL_LINE_STIPPLE_PATTERN'))
    State('glPolygonStipple', "", ("byte:32,4", None, bgl.glGetPolygonStipple))
    
    State('glDepthMask', "", ("int:1", 'GL_DEPTH_WRITEMASK'))
    
    State('glMatrixMode', "", ({'MODELVIEW', 'PROJECTION', 'TEXTURE'}, 'GL_MATRIX_MODE')) # bgl has no enums for COLOR matrix
    
    Matrix = mathutils.Matrix
    Buffer = bgl.Buffer
    range4 = tuple(range(4))
    int1buf = Buffer(bgl.GL_INT, 1)
    float1buf = Buffer(bgl.GL_FLOAT, 1)
    float2buf = Buffer(bgl.GL_FLOAT, 2)
    matrixbuf = Buffer(bgl.GL_FLOAT, 16)
    
    glGetIntegerv = getattr(bgl, "glGetIntegerv")
    glGetFloatv = getattr(bgl, "glGetFloatv")
    glMatrixMode = getattr(bgl, "glMatrixMode")
    glLoadMatrixf = getattr(bgl, "glLoadMatrixf")
    GL_MATRIX_MODE = getattr(bgl, "GL_MATRIX_MODE")
    
    def matrix_to_buffer(m, dtype=bgl.GL_FLOAT):
        return Buffer(dtype, 16, [m[i][j] for i in range4 for j in range4])
    def buffer_to_matrix(buf):
        return Matrix((buf[0:4], buf[4:8], buf[8:12], buf[12:16]))
    
    cgl.matrix_to_buffer = staticmethod(matrix_to_buffer)
    cgl.buffer_to_matrix = staticmethod(buffer_to_matrix)
    
    matrix_mode_map = {bgl.GL_MODELVIEW: bgl.GL_MODELVIEW_MATRIX, bgl.GL_PROJECTION: bgl.GL_PROJECTION_MATRIX, bgl.GL_TEXTURE: bgl.GL_TEXTURE_MATRIX}
    def _get(self, instance, owner):
        glGetIntegerv(GL_MATRIX_MODE, int1buf)
        glGetFloatv(matrix_mode_map[int1buf[0]], matrixbuf)
        return buffer_to_matrix(matrixbuf)
    def _set(self, instance, value):
        glLoadMatrixf(matrix_to_buffer(value))
    add_descriptor("Matrix", _get, _set)
    
    def add_specific_matrix_property(name, mode_enum, matrix_enum):
        def _get(self, instance, owner):
            glGetFloatv(matrix_enum, matrixbuf)
            return buffer_to_matrix(matrixbuf)
        def _set(self, instance, value):
            glGetIntegerv(GL_MATRIX_MODE, int1buf)
            glMatrixMode(mode_enum)
            glLoadMatrixf(matrix_to_buffer(value))
            glMatrixMode(int1buf[0])
        add_descriptor(name, _get, _set)
    add_specific_matrix_property("Matrix_ModelView", bgl.GL_MODELVIEW, bgl.GL_MODELVIEW_MATRIX)
    add_specific_matrix_property("Matrix_Projection", bgl.GL_PROJECTION, bgl.GL_PROJECTION_MATRIX)
    add_specific_matrix_property("Matrix_Texture", bgl.GL_TEXTURE, bgl.GL_TEXTURE_MATRIX)
    
    def _get(self, instance, owner):
        glGetFloatv(bgl.GL_POLYGON_OFFSET_FACTOR, float1buf)
        factor = float1buf[0]
        glGetFloatv(bgl.GL_POLYGON_OFFSET_UNITS, float1buf)
        units = float1buf[0]
        return (factor, units)
    def _set(self, instance, value):
        bgl.glPolygonOffset(value[0], value[1])
    add_descriptor("PolygonOffset", _get, _set)
    
    def _get(self, instance, owner):
        glGetFloatv(bgl.GL_DEPTH_RANGE, float2buf)
        zNear, zFar = float2buf[0], float2buf[1]
        return (zNear, zFar)
    def _set(self, instance, value):
        bgl.glDepthRange(value[0], value[1])
    add_descriptor("DepthRange", _get, _set)

fill_CGL()
del fill_CGL
