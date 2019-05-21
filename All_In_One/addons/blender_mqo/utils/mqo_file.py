import re
import math


ALLOWABLE_ERROR = 1e-5
INDENT = "    "


class RawData:
    def __init__(self, data):
        self.data = data
        self.seek = 0

    def get_line(self):
        idx = self.data[self.seek:].find(b'\n')
        start = self.seek
        end = self.seek + idx + 1
        self.seek = end

        return self.data[start:end]

    def eof(self):
        return len(self.data) == self.seek


def remove_return(line):
    for c in [b'\r', b'\n']:
        line = line.replace(c, b'')
    return line


def decode(str_):
    lookup = [
        "utf-8", "enc_jp", "euc_jis_2004", "euc_jisx0213", "shift_jis",
        "shift_jis_2004", "shift_jisx0213", "iso2022jp", "iso2022_jp_1",
        "iso2022_jp_2", "iso2022_jp_3", "iso2022_jp_ext", "latin_1", "ascii"
    ]
    for enc in lookup:
        try:
            decoded_str = str_.decode(enc)
            break
        except:
            pass
    else:
        raise RuntimeError("Failed to encoding.")

    return decoded_str


# pylint: disable=too-many-return-statements
def is_same(var1, var2, allowable_erorr=ALLOWABLE_ERROR):
    if (var1 is None) and (var2 is None):
        return True
    elif type(var1) != type(var2):  # pylint: disable=unidiomatic-typecheck
        return False
    elif isinstance(var1, int) and isinstance(var2, int):
        if var1 != var2:
            return False
    elif isinstance(var1, float) and isinstance(var2, float):
        if math.fabs(var1 - var2) > allowable_erorr:
            return False
    elif isinstance(var1, str) and isinstance(var2, str):
        if var1 != var2:
            return False
    elif isinstance(var1, list) and isinstance(var2, list):
        for elm1, elm2 in zip(var1, var2):
            if not is_same(elm1, elm2):
                return False
    else:
        raise RuntimeError("Not supported type (var1: {}, var2: {})"
                           .format(type(var1), type(var2)))
    return True


class DirLight:
    def __init__(self):
        self._dir = None
        self._color = None

    @property
    def dir(self):
        if self._dir is None:
            return [0.408, 0.408, 0.816]
        return self._dir

    @dir.setter
    def dir(self, dir_):
        self._dir = dir_

    @property
    def color(self):
        if self._color is None:
            return [1.0, 1.0, 1.0]
        return self._color

    @color.setter
    def color(self, color_):
        self._color = color_

    def is_same(self, other, allowable_error=ALLOWABLE_ERROR):
        self_keys = list(self.__dict__.keys())
        other_keys = list(other.__dict__.keys())

        if len(self_keys) != len(other_keys):
            return False

        for key in self_keys:
            if key not in other_keys:
                return False
            if not is_same(self.__dict__[key], other.__dict__[key],
                           allowable_error):
                return False

        return True

    def to_str(self, fmt='STDOUT'):
        s = ""
        if fmt == 'MQO_FILE':
            s += INDENT * 2 + "light {\n"
            s += INDENT * 3 + "dir {:.3f} {:.3f} {:.3f}\n".format(*self._dir)
            s += INDENT * 3 + "color {:.3f} {:.3f} {:.3f}\n"\
                              .format(*self._color)
            s += INDENT * 2 + "}\n"
        return s

    def set_default_params(self):
        self._dir = [0.408, 0.408, 0.816]
        self._color = [1.0, 1.0, 1.0]


class Scene:
    def __init__(self):
        self._pos = None
        self._lookat = None
        self._head = None
        self._pich = None
        self._bank = None
        self._ortho = None
        self._zoom2 = None
        self._amb = None
        self._frontclip = None
        self._backclip = None
        self._dirlights = []

    @property
    def pos(self):
        if self._pos is None:
            return [0, 0, 1500]
        return self._pos

    @pos.setter
    def pos(self, pos_):
        self._pos = pos_

    @property
    def lookat(self):
        if self._lookat is None:
            return [0, 0, 0]
        return self._lookat

    @lookat.setter
    def lookat(self, lookat_):
        self._lookat = lookat_

    @property
    def head(self):
        if self._head is None:
            return -0.5236
        return self._head

    @head.setter
    def head(self, head_):
        self._head = head_

    @property
    def pich(self):
        if self._pich is None:
            return 0.5236
        return self._pich

    @pich.setter
    def pich(self, pich_):
        self._pich = pich_

    @property
    def bank(self):
        if self._bank is None:
            return 0.0
        return self._bank

    @bank.setter
    def bank(self, bank_):
        self._bank = bank_

    @property
    def ortho(self):
        if self._ortho is None:
            return 0
        return self._ortho

    @ortho.setter
    def ortho(self, ortho_):
        self._ortho = ortho_

    @property
    def zoom2(self):
        if self._zoom2 is None:
            return 5.0
        return self._zoom2

    @zoom2.setter
    def zoom2(self, zoom2_):
        self._zoom2 = zoom2_

    @property
    def amb(self):
        if self._amb is None:
            return [0.25, 0.25, 0.25]
        return self._amb

    @amb.setter
    def amb(self, amb_):
        self._amb = amb_

    @property
    def frontclip(self):
        if self._frontclip is None:
            return 225.00002
        return self._frontclip

    @frontclip.setter
    def frontclip(self, frontclip_):
        self._frontclip = frontclip_

    @property
    def backclip(self):
        if self._backclip is None:
            return 45000
        return self._backclip

    @backclip.setter
    def backclip(self, backclip_):
        self._backclip = backclip_

    def add_dirlight(self, light):
        self._dirlights.append(light)

    def is_same(self, other, allowable_error=ALLOWABLE_ERROR):
        self_keys = list(self.__dict__.keys())
        other_keys = list(other.__dict__.keys())

        if len(self_keys) != len(other_keys):
            return False

        self_keys.remove("dirlights")
        other_keys.remove("dirlights")

        for key in self_keys:
            if key not in other_keys:
                return False
            if not is_same(self.__dict__[key], other.__dict__[key],
                           allowable_error):
                return False

        for sd, od in zip(self._dirlights, other.dirlights):
            if not sd.is_same(od):
                return False

        return True

    def to_str(self, fmt='STDOUT'):
        s = ""
        if fmt == 'MQO_FILE':
            s += "Scene {\n"
            if self._pos is not None:
                s += INDENT + "pos {:.4f} {:.4f} {:.4f}\n".format(*self._pos)
            if self._lookat is not None:
                s += INDENT + "lookat {:.4f} {:.4f} {:.4f}\n"\
                     .format(*self._lookat)
            if self._head is not None:
                s += INDENT + "head {:.4f}\n".format(self._head)
            if self._pich is not None:
                s += INDENT + "pich {:.4f}\n".format(self._pich)
            if self._bank is not None:
                s += INDENT + "bank {:.4f}\n".format(self._bank)
            if self._ortho is not None:
                s += INDENT + "ortho {}\n".format(self._ortho)
            if self._zoom2 is not None:
                s += INDENT + "zoom2 {:.4f}\n".format(self._zoom2)
            if self._amb is not None:
                s += INDENT + "amb {:.3f} {:.3f} {:.3f}\n".format(*self._amb)
            if self._frontclip is not None:
                s += INDENT + "frontclip {:.5f}\n".format(self._frontclip)
            if self._backclip is not None:
                s += INDENT + "backclip {}\n".format(self._backclip)
            if len(self._dirlights) > 0:
                s += INDENT + "dirlight {}".format(len(self._dirlights)) + \
                     " {\n"
                for light in self._dirlights:
                    s += light.to_str(fmt)
                s += INDENT + "}\n"
            s += "}\n"

        return s

    def set_default_params(self):
        self._pos = [0, 0, 1500]
        self._lookat = [0, 0, 0]
        self._head = -0.5236
        self._pich = 0.5236
        self._bank = 0.0
        self._ortho = 0
        self._zoom2 = 5.0
        self._amb = [0.25, 0.25, 0.25]
        self._frontclip = 225.00002
        self._backclip = 45000
        light = DirLight()
        light.set_default_params()
        self._dirlights.append(light)


class Material:
    def __init__(self):
        self._name = None
        self._shader = None
        self._vertex_color = None
        self._doubles = None
        self._color = None
        self._diffuse = None
        self._ambient = None
        self._emissive = None
        self._specular = None
        self._power = None
        self._reflect = None
        self._refract = None
        self._texture_map = None
        self._alpha_plane_map = None
        self._bump_map = None
        self._projection_type = None
        self._projection_pos = None
        self._projection_scale = None
        self._projection_angle = None

    @property
    def name(self):
        if self._name is None:
            return "mat1"
        return self._name

    @name.setter
    def name(self, name_):
        self._name = name_

    @property
    def shader(self):
        if self._shader is None:
            return 3
        return self._shader

    @shader.setter
    def shader(self, shader_):
        self._shader = shader_

    @property
    def vertex_color(self):
        if self._vertex_color is None:
            return None
        return self._vertex_color

    @vertex_color.setter
    def vertex_color(self, vertex_color_):
        self._vertex_color = vertex_color_

    @property
    def doubles(self):
        if self._doubles is None:
            return None
        return self._doubles

    @doubles.setter
    def doubles(self, doubles_):
        self._doubles = doubles_

    @property
    def color(self):
        if self._color is None:
            return [1.0, 1.0, 1.0, 1.0]
        return self._color

    @color.setter
    def color(self, color_):
        self._color = color_

    @property
    def diffuse(self):
        if self._diffuse is None:
            return 0.8
        return self._diffuse

    @diffuse.setter
    def diffuse(self, diffuse_):
        self._diffuse = diffuse_

    @property
    def ambient(self):
        if self._ambient is None:
            return 0.6
        return self._ambient

    @ambient.setter
    def ambient(self, ambient_):
        self._ambient = ambient_

    @property
    def emissive(self):
        if self._emissive is None:
            return 0.0
        return self._emissive

    @emissive.setter
    def emissive(self, emissive_):
        self._emissive = emissive_

    @property
    def specular(self):
        if self._specular is None:
            return 0.0
        return self._specular

    @specular.setter
    def specular(self, specular_):
        self._specular = specular_

    @property
    def power(self):
        if self._power is None:
            return 5.0
        return self._power

    @power.setter
    def power(self, power_):
        self._power = power_

    @property
    def reflect(self):
        if self._reflect is None:
            return None
        return self._reflect

    @reflect.setter
    def reflect(self, reflect_):
        self._reflect = reflect_

    @property
    def refract(self):
        if self._refract is None:
            return None
        return self._refract

    @refract.setter
    def refract(self, refract_):
        self._refract = refract_

    @property
    def texture_map(self):
        if self._texture_map is None:
            return None
        return self._texture_map

    @texture_map.setter
    def texture_map(self, texture_map_):
        self._texture_map = texture_map_

    @property
    def alpha_plane_map(self):
        if self._alpha_plane_map is None:
            return None
        return self._alpha_plane_map

    @alpha_plane_map.setter
    def alpha_plane_map(self, alpha_plane_map_):
        self._alpha_plane_map = alpha_plane_map_

    @property
    def bump_map(self):
        if self._bump_map is None:
            return None
        return self._bump_map

    @bump_map.setter
    def bump_map(self, bump_map_):
        self._bump_map = bump_map_

    @property
    def projection_type(self):
        if self._projection_type is None:
            return None
        return self._projection_type

    @projection_type.setter
    def projection_type(self, projection_type_):
        self._projection_type = projection_type_

    @property
    def projection_pos(self):
        if self._projection_pos is None:
            return None
        return self._projection_pos

    @projection_pos.setter
    def projection_pos(self, projection_pos_):
        self._projection_pos = projection_pos_

    @property
    def projection_scale(self):
        if self._projection_scale is None:
            return None
        return self._projection_scale

    @projection_scale.setter
    def projection_scale(self, projection_scale_):
        self._projection_scale = projection_scale_

    @property
    def projection_angle(self):
        if self._projection_angle is None:
            return None
        return self._projection_angle

    @projection_angle.setter
    def projection_angle(self, projection_angle_):
        self._projection_angle = projection_angle_

    def is_same(self, other, allowable_error=ALLOWABLE_ERROR):
        self_keys = list(self.__dict__.keys())
        other_keys = list(other.__dict__.keys())

        if len(self_keys) != len(other_keys):
            return False

        for key in self_keys:
            if key not in other_keys:
                return False
            if not is_same(self.__dict__[key], other.__dict__[key],
                           allowable_error):
                return False

        return True

    def to_str(self, fmt='STDOUT'):
        s = ""
        if fmt == 'MQO_FILE':
            s = INDENT + "\"{}\"".format(self._name)
            if self._shader is not None:
                s += " shader({})".format(self._shader)
            if self._vertex_color is not None:
                s += " vcol({})".format(self._vertex_color)
            if self._doubles is not None:
                s += " dbls({})".format(self._doubles)
            if self._color is not None:
                s += " col({:.3f} {:.3f} {:.3f} {:.3f})"\
                     .format(*self._color)
            if self._diffuse is not None:
                s += " dif({:.3f})".format(self._diffuse)
            if self._ambient is not None:
                s += " amb({:.3f})".format(self._ambient)
            if self._emissive is not None:
                s += " emi({:.3f})".format(self._emissive)
            if self._specular is not None:
                s += " spc({:.3f})".format(self.specular)
            if self._power is not None:
                s += " power({:.2f})".format(self._power)
            if self._reflect is not None:
                s += " reflect({:.3f})".format(self._reflect)
            if self._refract is not None:
                s += " refract({:.3f})".format(self._refract)
            if self._texture_map is not None:
                s += " tex(\"{}\")".format(self._texture_map)
            if self._alpha_plane_map is not None:
                s += " aplane(\"{}\")".format(self._alpha_plane_map)
            if self._bump_map is not None:
                s += " bump(\"{}\")".format(self._bump_map)
            if self._projection_type is not None:
                s += " proj_type({})".format(self._projection_type)
            if self._projection_pos is not None:
                s += " proj_pos({:.3f} {:.3f} {:.3f})"\
                     .format(*self._projection_pos)
            if self._projection_scale is not None:
                s += " proj_scale({:.3f} {:.3f} {:.3f})"\
                     .format(*self._projection_scale)
            if self._projection_angle is not None:
                s += " proj_pos({:.3f} {:.3f} {:.3f})"\
                     .format(*self._projection_angle)
            s += "\n"

        return s

    def set_default_params(self):
        self._name = "mat1"
        self._shader = 3
        self._vertex_color = None
        self._doubles = None
        self._color = [1.0, 1.0, 1.0, 1.0]
        self._diffuse = 0.8
        self._ambient = 0.6
        self._emissive = 0.0
        self._specular = 0.0
        self._power = 5.0
        self._reflect = None
        self._refract = None
        self._texture_map = None
        self._alpha_plane_map = None
        self._bump_map = None
        self._projection_type = None
        self._projection_pos = None
        self._projection_scale = None
        self._projection_angle = None


class Face:
    def __init__(self):
        self._ngons = None
        self._vertex_indices = None
        self._material = None
        self._uv_coords = None
        self._colors = None
        self._crs = None

    @property
    def ngons(self):
        if self._ngons is None:
            return None
        return self._ngons

    @ngons.setter
    def ngons(self, ngons_):
        self._ngons = ngons_

    @property
    def vertex_indices(self):
        if self._vertex_indices is None:
            return None
        return self._vertex_indices

    @vertex_indices.setter
    def vertex_indices(self, vertex_indices_):
        self._vertex_indices = vertex_indices_

    @property
    def material(self):
        if self._material is None:
            return None
        return self._material

    @material.setter
    def material(self, material_):
        self._material = material_

    @property
    def uv_coords(self):
        if self._uv_coords is None:
            return None
        return self._uv_coords

    @uv_coords.setter
    def uv_coords(self, uv_coords_):
        self._uv_coords = uv_coords_

    @property
    def colors(self):
        if self._colors is None:
            return None
        return self._colors

    @colors.setter
    def colors(self, colors_):
        self._colors = colors_

    @property
    def crs(self):
        if self._crs is None:
            return None
        return self._crs

    @crs.setter
    def crs(self, crs_):
        self._crs = crs_

    def is_same(self, other, allowable_error=ALLOWABLE_ERROR):
        self_keys = list(self.__dict__.keys())
        other_keys = list(other.__dict__.keys())

        if len(self_keys) != len(other_keys):
            return False

        for key in self_keys:
            if key not in other_keys:
                return False
            if not is_same(self.__dict__[key], other.__dict__[key],
                           allowable_error):
                return False

        return True

    def to_str(self, fmt='STDOUT'):
        s = ""
        if fmt == 'MQO_FILE':
            s += INDENT * 2 + "{}".format(self._ngons)
            if self._vertex_indices is not None:
                vert_indices_str = [str(idx)
                                    for idx in self._vertex_indices]
                s += " V({})".format(" ".join(vert_indices_str))
            if self._material is not None:
                s += " M({})".format(self._material)
            if self._uv_coords is not None:
                coords = [x for uv in self._uv_coords for x in uv]
                coords_str = ["{:.5f}".format(c) for c in coords]
                s += " UV({})".format(" ".join(coords_str))
            if self._colors is not None:
                colors = ["{}".format(c) for c in self._colors]
                s += " COL({})".format(" ".join(colors))
            if self._crs is not None:
                crs = ["{}".format(c) for c in self._crs]
                s += " CRS({})".format(" ".join(crs))
            s += "\n"

        return s


class Object:
    def __init__(self):
        self._name = None
        self._uid = None
        self._depth = None
        self._folding = None
        self._scale = None
        self._rotation = None
        self._translation = None
        self._patch = None
        self._patch_triangle = None
        self._segment = None
        self._visible = None
        self._locking = None
        self._shading = None
        self._facet = None
        self._color = None
        self._color_type = None
        self._mirror = None
        self._mirror_axis = None
        self._mirror_distance = None
        self._lathe = None
        self._lathe_axis = None
        self._lathe_segment = None
        self._normal_weight = None
        self._vertices = []
        self._faces = []

    @property
    def name(self):
        if self._name is None:
            return "obj1"
        return self._name

    @name.setter
    def name(self, name_):
        self._name = name_

    @property
    def uid(self):
        if self._uid is None:
            return None
        return self._uid

    @uid.setter
    def uid(self, uid_):
        self._uid = uid_

    @property
    def depth(self):
        if self._depth is None:
            return 0
        return self._depth

    @depth.setter
    def depth(self, depth_):
        self._depth = depth_

    @property
    def folding(self):
        if self._folding is None:
            return 0
        return self._folding

    @folding.setter
    def folding(self, folding_):
        self._folding = folding_

    @property
    def scale(self):
        if self._scale is None:
            return [1.0, 1.0, 1.0]
        return self._scale

    @scale.setter
    def scale(self, scale_):
        self._scale = scale_

    @property
    def rotation(self):
        if self._rotation is None:
            return [0.0, 0.0, 0.0]
        return self._rotation

    @rotation.setter
    def rotation(self, rotation_):
        self._rotation = rotation_

    @property
    def translation(self):
        if self._translation is None:
            return [0.0, 0.0, 0.0]
        return self._translation

    @translation.setter
    def translation(self, translation_):
        self._translation = translation_

    @property
    def patch(self):
        if self._patch is None:
            return None
        return self._patch

    @patch.setter
    def patch(self, patch_):
        self._patch = patch_

    @property
    def patch_triangle(self):
        if self._patch_triangle is None:
            return None
        return self._patch_triangle

    @patch_triangle.setter
    def patch_triangle(self, patch_triangle_):
        self._patch_triangle = patch_triangle_

    @property
    def segment(self):
        if self._segment is None:
            return None
        return self._segment

    @segment.setter
    def segment(self, segment_):
        self._segment = segment_

    @property
    def visible(self):
        if self._visible is None:
            return 15
        return self._visible

    @visible.setter
    def visible(self, visible_):
        self._visible = visible_

    @property
    def locking(self):
        if self._locking is None:
            return 0
        return self._locking

    @locking.setter
    def locking(self, locking_):
        self._locking = locking_

    @property
    def shading(self):
        if self._shading is None:
            return 1
        return self._shading

    @shading.setter
    def shading(self, shading_):
        self._shading = shading_

    @property
    def facet(self):
        if self._facet is None:
            return 59.5
        return self._facet

    @facet.setter
    def facet(self, facet_):
        self._facet = facet_

    @property
    def color(self):
        if self._color is None:
            return [0.898, 0.498, 0.698]
        return self._color

    @color.setter
    def color(self, color_):
        self._color = color_

    @property
    def color_type(self):
        if self._color_type is None:
            return 0
        return self._color_type

    @color_type.setter
    def color_type(self, color_type_):
        self._color_type = color_type_

    @property
    def mirror(self):
        if self._mirror is None:
            return None
        return self._mirror

    @mirror.setter
    def mirror(self, mirror_):
        self._mirror = mirror_

    @property
    def mirror_axis(self):
        if self._mirror_axis is None:
            return None
        return self._mirror_axis

    @mirror_axis.setter
    def mirror_axis(self, mirror_axis_):
        self._mirror_axis = mirror_axis_

    @property
    def mirror_distance(self):
        if self._mirror_distance is None:
            return None
        return self._mirror_distance

    @mirror_distance.setter
    def mirror_distance(self, mirror_distance_):
        self._mirror_distance = mirror_distance_

    @property
    def lathe(self):
        if self._lathe is None:
            return None
        return self._lathe

    @lathe.setter
    def lathe(self, lathe_):
        self._lathe = lathe_

    @property
    def lathe_axis(self):
        if self._lathe_axis is None:
            return None
        return self._lathe_axis

    @lathe_axis.setter
    def lathe_axis(self, lathe_axis_):
        self._lathe_axis = lathe_axis_

    @property
    def lathe_segment(self):
        if self._lathe_segment is None:
            return None
        return self._lathe_segment

    @lathe_segment.setter
    def lathe_segment(self, lathe_segment_):
        self._lathe_segment = lathe_segment_

    @property
    def normal_weight(self):
        if self._normal_weight is None:
            return 1
        return self._normal_weight

    @normal_weight.setter
    def normal_weight(self, normal_weight_):
        self._normal_weight = normal_weight_

    def add_vertex(self, vertex):
        self._vertices.append(vertex)

    def add_vertices(self, vertices):
        for v in vertices:
            self._vertices.append(v)

    def get_vertices(self):
        return self._vertices

    def add_face(self, face):
        self._faces.append(face)

    def add_faces(self, faces):
        for f in faces:
            self._faces.append(f)

    def get_faces(self, uniq=False):
        if uniq is False:
            return self._faces

        faces = []
        for f1 in self._faces:
            f1_vertex_indices = set(f1.vertex_indices)
            for f2 in faces:
                if f1_vertex_indices == set(f2.vertex_indices):
                    break
            else:
                faces.append(f1)

        return faces

    def is_same(self, other, allowable_error=ALLOWABLE_ERROR):
        self_keys = list(self.__dict__.keys())
        other_keys = list(other.__dict__.keys())

        if len(self_keys) != len(other_keys):
            return False

        self_keys.remove("vertices")
        self_keys.remove("faces")
        other_keys.remove("vertices")
        other_keys.remove("faces")

        for key in self_keys:
            if key not in other_keys:
                return False
            if not is_same(self.__dict__[key], other.__dict__[key],
                           allowable_error):
                return False

        for sv, ov in zip(self._vertices, other.vertices):
            if not is_same(sv, ov):
                return False

        for sf, of in zip(self._faces, other.faces):
            if not sf.is_same(of):
                return False

        return True

    def to_str(self, fmt='STDOUT'):
        s = ""

        if fmt == 'MQO_FILE':
            s += "Object \"{}\"".format(self._name) + " {\n"
            if self._uid is not None:
                s += INDENT + "uid {}\n".format(self._uid)
            if self._depth is not None:
                s += INDENT + "depth {}\n".format(self._depth)
            if self._folding is not None:
                s += INDENT + "folding {}\n".format(self._folding)
            if self._scale is not None:
                s += INDENT + "scale {:.6f} {:.6f} {:.6f}\n"\
                     .format(*self._scale)
            if self._rotation is not None:
                s += INDENT + "rotation {:.6f} {:.6f} {:.6f}\n"\
                     .format(*self._rotation)
            if self._translation is not None:
                s += INDENT + "translation {:.6f} {:.6f} {:.6f}\n"\
                     .format(*self._translation)
            if self._patch is not None:
                s += INDENT + "patch {}\n".format(self._patch)
            if self._patch_triangle is not None:
                s += INDENT + "patchtri {}\n".format(self._patch_triangle)
            if self._segment is not None:
                s += INDENT + "segment {}\n".format(self._segment)
            if self._visible is not None:
                s += INDENT + "visible {}\n".format(self._visible)
            if self._locking is not None:
                s += INDENT + "locking {}\n".format(self._locking)
            if self._shading is not None:
                s += INDENT + "shading {}\n".format(self._shading)
            if self._facet is not None:
                s += INDENT + "facet {:.1f}\n".format(self._facet)
            if self._color is not None:
                s += INDENT + "color {:.3f} {:.3f} {:.3f}\n"\
                     .format(*self._color)
            if self._color_type is not None:
                s += INDENT + "color_type {}\n".format(self._color_type)
            if self._mirror is not None:
                s += INDENT + "mirror {}\n".format(self._mirror)
            if self._mirror_axis is not None:
                s += INDENT + "mirror_axis {}\n".format(self._mirror_axis)
            if self._mirror_distance is not None:
                s += INDENT + "mirror_dis {:.3f}\n"\
                     .format(self._mirror_distance)
            if self._lathe is not None:
                s += INDENT + "lathe {}\n".format(self._lathe)
            if self._lathe_axis is not None:
                s += INDENT + "lathe_axis {}\n".format(self._lathe_axis)
            if self._lathe_segment is not None:
                s += INDENT + "lathe_seg {}\n".format(self._lathe_segment)
            if self._normal_weight is not None:
                s += INDENT + "normal_weight {}\n".format(self._normal_weight)
            if len(self._vertices) > 0:
                s += INDENT + "vertex {}".format(len(self._vertices)) + " {\n"
                for vert in self._vertices:
                    s += INDENT * 2 + "{:.4f} {:.4f} {:.4f}\n".format(*vert)
                s += INDENT + "}\n"
            if len(self._faces) > 0:
                s += INDENT + "face {}".format(len(self._faces)) + " {\n"
                for face in self._faces:
                    s += face.to_str(fmt)
                s += INDENT + "}\n"
            s += "}\n"

        return s

    def set_default_params(self):
        self._name = "obj1"
        self._uid = None
        self._depth = 0
        self._folding = 0
        self._scale = [1, 1, 1]
        self._rotation = [0, 0, 0]
        self._translation = [0, 0, 0]
        self._patch = None
        self._patch_triangle = None
        self._segment = None
        self._visible = 15
        self._locking = 0
        self._shading = 1
        self._facet = 59.5
        self._color = [0.898, 0.498, 0.698]
        self._color_type = 0
        self._mirror = None
        self._mirror_axis = None
        self._mirror_distance = None
        self._lathe = None
        self._lathe_axis = None
        self._lathe_segment = None
        self._normal_weight = 1
        self._vertices = []
        self._faces = []


class MqoFile:
    def __init__(self):
        self._raw = None

        # .mqo data structure
        self._header = None
        self._version = None
        self._format = None
        self._scene = None
        self._materials = []
        self._objects = []

    def __repr__(self):
        s = "Header: {}\n".format(self._header)
        s += "Version: {}\n".format(self._version)
        s += "Format: {}\n\n".format(self._format)
        s += self._scene.to_str(fmt='MQO_FILE')
        s += "\n"
        for mtrl in self._materials:
            s += mtrl.to_str(fmt='MQO_FILE')
            s += "\n"
        for obj in self._objects:
            s += obj.to_str(fmt='MQO_FILE')
            s += "\n"

        return s

    @property
    def header(self):
        if self._header:
            return None
        return self._header

    @header.setter
    def header(self, header_):
        self._header = header_

    @property
    def version(self):
        if self._version is None:
            return None
        return self._version

    @version.setter
    def version(self, version_):
        self._version = version_

    @property
    def format(self):
        if self._format is None:
            return None
        return self._format

    @format.setter
    def format(self, format_):
        self._format = format_

    @property
    def scene(self):
        if self._scene is None:
            return None
        return self._scene

    @scene.setter
    def scene(self, scene_):
        self._scene = scene_

    def get_materials(self):
        return self._materials

    def add_material(self, material):
        self._materials.append(material)

    def get_objects(self):
        return self._objects

    def add_object(self, object_):
        self._objects.append(object_)

    # pylint: disable=too-many-return-statements
    def is_same(self, other, allowable_error=ALLOWABLE_ERROR):
        self_keys = list(self.__dict__.keys())
        other_keys = list(other.__dict__.keys())

        if len(self_keys) != len(other_keys):
            return False

        self_keys.remove("scene")
        self_keys.remove("materials")
        self_keys.remove("objects")
        self_keys.remove("raw")
        other_keys.remove("scene")
        other_keys.remove("materials")
        other_keys.remove("objects")
        other_keys.remove("raw")

        for key in self_keys:
            if key not in other_keys:
                return False
            if self_keys != other_keys:
                return False

        for key in self_keys:
            if key not in other_keys:
                return False
            if not is_same(self.__dict__[key], other.__dict__[key],
                           allowable_error):
                return False

        if not self._scene.is_same(other.scene):
            return False

        for so, oo in zip(self._objects, other.objects):
            if not so.is_same(oo):
                return False

        for sm, om in zip(self._materials, other.materials):
            if not sm.is_same(om):
                return False

        return True

    def _parse_thumbnail(self, first_line):
        if first_line.find(b"Thumbnail ") == -1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

        while not self._raw.eof():
            line = self._raw.get_line()
            line = remove_return(line)
            line = line.strip()
            if line.find(b"}"):
                return

        raise RuntimeError("Format Error: Failed to parse 'Thumbnail' field")

    def _parse_light(self, first_line):
        if first_line.find(b"light {") == -1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

        def parse(l, rgx):
            r = re.compile(rgx)
            m = r.search(l)
            if not m:
                raise RuntimeError("Failed to parse. (line:{})".format(l))
            return m.groups()

        light = DirLight()
        while not self._raw.eof():
            line = self._raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                return light

            if line.find(b"dir") != -1:
                rgx = rb"dir ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)"
                light.dir = [float(s) for s in parse(line, rgx)]
            elif line.find(b"color") != -1:
                rgx = rb"color ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)"
                light.color = [float(s) for s in parse(line, rgx)]

        raise RuntimeError("Format Error: Failed to parse 'light' field")

    def _parse_dirlights(self, first_line):
        r = re.compile(rb"dirlights ([0-9]+) {")
        m = r.search(first_line)
        if not m or len(m.groups()) != 1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))
        num_light = int(m.group(1))

        lights = []
        while not self._raw.eof():
            line = self._raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                if len(lights) != num_light:
                    raise RuntimeError(
                        "Incorrect number of lights. (expects {} but {})"
                        .format(num_light, len(lights)))
                return lights

            if line.find(b"light") != -1:
                lights.append(self._parse_light(line))

        raise RuntimeError("Format Error: Failed to parse 'dirlights' field")

    def _parse_scene(self, first_line):
        if first_line.find(b"Scene {") == -1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

        def parse(l, rgx):
            r = re.compile(rgx)
            m = r.search(l)
            if not m:
                raise RuntimeError("Failed to parse. (line:{})".format(l))
            return m.groups()

        scene = Scene()
        while not self._raw.eof():
            line = self._raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                return scene

            if line.find(b"pos") != -1:
                rgx = rb"pos ([-0-9\.]+) ([-0-9\.]+) ([-0-9\.]+)"
                scene.pos = [float(s) for s in parse(line, rgx)]
            elif line.find(b"lookat") != -1:
                rgx = rb"lookat ([-0-9\.]+) ([-0-9\.]+) ([-0-9\.]+)"
                scene.lookat = [float(s) for s in parse(line, rgx)]
            elif line.find(b"head") != -1:
                rgx = rb"head ([-0-9\.]+)"
                scene.head = float(parse(line, rgx)[0])
            elif line.find(b"pich") != -1:
                rgx = rb"pich ([-0-9\.]+)"
                scene.pich = float(parse(line, rgx)[0])
            elif line.find(b"bank") != -1:
                rgx = rb"bank ([-0-9\.]+)"
                scene.bank = float(parse(line, rgx)[0])
            elif line.find(b"ortho") != -1:
                rgx = rb"ortho ([0-9\.]+)"
                scene.ortho = float(parse(line, rgx)[0])
            elif line.find(b"zoom2") != -1:
                rgx = rb"zoom2 ([0-9\.]+)"
                scene.zoom2 = float(parse(line, rgx)[0])
            elif line.find(b"amb") != -1:
                rgx = rb"amb ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)"
                scene.amb = [float(s) for s in parse(line, rgx)]
            elif line.find(b"frontclip") != -1:
                rgx = rb"frontclip ([0-9\.]+)"
                scene.frontclip = float(parse(line, rgx)[0])
            elif line.find(b"backclip") != -1:
                rgx = rb"backclip ([0-9\.]+)"
                scene.backclip = float(parse(line, rgx)[0])
            elif line.find(b"dirlights") != -1:
                scene.add_dirlight(self._parse_dirlights(line))

        raise RuntimeError("Format Error: Failed to parse 'Scene' field.")

    def _parse_material(self, first_line):
        r = re.compile(rb"Material ([0-9]+) {")
        m = r.search(first_line)
        if not m or len(m.groups()) != 1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))
        num_mtrl = int(m.group(1))

        def parse(l, rgx):
            r = re.compile(rgx)
            m = r.search(l)
            if not m:
                return None
            return m.groups()

        mtrls = []
        while not self._raw.eof():
            line = self._raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                if num_mtrl != len(mtrls):
                    raise RuntimeError(
                        "Incorrect number of materials. (expects {} but {})"
                        .format(num_mtrl, len(mtrls)))
                return mtrls

            mtrl = Material()

            pattern = rb"\"([^\"]*)\""
            r = re.compile(pattern)
            m = r.search(line)
            if not m:
                raise RuntimeError("Failed to find material name. (line:{})"
                                   .format(line))
            mtrl.name = decode(m.group(1))

            result = parse(line, rb"\"[^\"]*\" .*shader\(([0-4])\)")
            if result:
                mtrl.shader = int(result[0])
            result = parse(line, rb"\"[^\"]*\" .*vcol\(([0-1])\)")
            if result:
                mtrl.vertex_color = int(result[0])
            result = parse(line, rb"\"[^\"]*\" .*dbls\(([0-1])\)")
            if result:
                mtrl.doubles = int(result[0])
            result = parse(line, rb"\"[^\"]*\" .*col\(([0-1]\.[0-9]+) "
                                 rb"([0-1]\.[0-9]+) ([0-1]\.[0-9]+) "
                                 rb"([0-1]\.[0-9]+)\)")
            if result:
                mtrl.color = [float(v) for v in result]
            result = parse(line, rb"\"[^\"]*\" .*dif\(([0-1]\.[0-9]+)\)")
            if result:
                mtrl.diffuse = float(result[0])
            result = parse(line, rb"\"[^\"]*\" .*amb\(([0-1]\.[0-9]+)\)")
            if result:
                mtrl.ambient = float(result[0])
            result = parse(line, rb"\"[^\"]*\" .*emi\(([0-1]\.[0-9]+)\)")
            if result:
                mtrl.emissive = float(result[0])
            result = parse(line, rb"\"[^\"]*\" .*spc\(([0-1]\.[0-9]+)\)")
            if result:
                mtrl.specular = float(result[0])
            result = parse(line, rb"\"[^\"]*\" .*power\(([0-9]+\.[0-9]+)\)")
            if result:
                mtrl.power = float(result[0])
            result = parse(line, rb"\"[^\"]*\" .*reflect\(([0-1]\.[0-9]+)\)")
            if result:
                mtrl.reflect = float(result[0])
            result = parse(line, rb"\"[^\"]*\" .*refract\(([1-5]\.[0-9]+)\)")
            if result:
                mtrl.refract = float(result[0])
            result = parse(line, rb"\"[^\"]*\" .*tex\(\"([^\)]+)\"\)")
            if result:
                mtrl.texture_map = decode(result[0])
            result = parse(line, rb"\"[^\"]*\" .*aplane\(\"([^\)]+)\"\)")
            if result:
                mtrl.alpha_plane_map = decode(result[0])
            result = parse(line, rb"\"[^\"]*\" .*bump\(\"([^\)]+)\"\)")
            if result:
                mtrl.bump_map = decode(result[0])
            result = parse(line, rb"\"[^\"]*\" .*proj_type\(([0-3])\)")
            if result:
                mtrl.projection_type = int(result[0])
            result = parse(line, rb"\"[^\"]*\" .*proj_pos\((-?[0-9]+\.[0-9]+) "
                                 rb"(-?[0-9]+\.[0-9]+) (-?[0-9]+\.[0-9]+)")
            if result:
                mtrl.projection_pos = [float(v) for v in result]
            result = parse(line, rb"\"[^\"]*\" "
                                 rb".*proj_scale\((-?[0-9]+\.[0-9]+) "
                                 rb"(-?[0-9]+\.[0-9]+) (-?[0-9]+\.[0-9]+)")
            if result:
                mtrl.projection_scale = [float(v) for v in result]
            result = parse(line, rb"\"[^\"]*\" "
                                 rb".*proj_angle\((-?[0-9]+\.[0-9]+) "
                                 rb"(-?[0-9]+\.[0-9]+) (-?[0-9]+\.[0-9]+)")
            if result:
                mtrl.projection_angle = [float(v) for v in result]

            mtrls.append(mtrl)

        raise RuntimeError("Format Error: Failed to parse 'Material' field.")

    def _parse_vertex(self, first_line):
        r = re.compile(rb"vertex ([0-9]+) {")
        m = r.search(first_line)
        if not m or len(m.groups()) != 1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

        num_verts = int(m.group(1))
        verts = []
        while not self._raw.eof():
            line = self._raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                if num_verts != len(verts):
                    raise RuntimeError("Number of Vertices does not match "
                                       "(expects {}, but {})"
                                       .format(num_verts, len(verts)))
                return verts

            r = re.compile(rb"([-0-9\.]+) ([-0-9\.]+) ([-0-9\.]+)")
            m = r.search(line)
            if not m or len(m.groups()) != 3:
                raise RuntimeError("Invalid format. (line:{})".format(line))

            verts.append([float(elm) for elm in m.groups()])

        raise RuntimeError("Format Error: Failed to parse 'vertex' field.")

    def _parse_face(self, first_line):
        r = re.compile(rb"face ([0-9]+) {")
        m = r.search(first_line)
        if not m or len(m.groups()) != 1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

        def parse(l, rgx):
            r = re.compile(rgx)
            m = r.search(l)
            if not m:
                return None
            return m.groups()

        num_faces = int(m.group(1))
        faces = []
        while not self._raw.eof():
            line = self._raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                if num_faces != len(faces):
                    raise RuntimeError("Number of Faces does not match "
                                       "(expects {}, but {})"
                                       .format(num_faces, len(faces)))
                return faces

            pattern = rb"([0-9]+)"
            r = re.compile(pattern)
            m = r.search(line)
            if not m:
                raise RuntimeError("Failed to find material name. (line:{})"
                                   .format(line))

            face = Face()
            face.ngons = int(m.group(1))

            result = parse(line, rb"[0-9]+.* V\(([-0-9\. ]+)\)")
            if result:
                face.vertex_indices = [
                    int(vidx) for vidx in decode(result[0]).split(" ")]
                if face.ngons != len(face.vertex_indices):
                    raise RuntimeError("Number of Vertices does not match "
                                       "(expects {}, but {}"
                                       .format(face.ngons,
                                               len(face.vertex_indices)))

            result = parse(line, rb"[0-9]+.* M\(([0-9 ]+)\)")
            if result:
                face.material = int(result[0])

            result = parse(line, rb"[0-9]+.* UV\(([0-9\. ]+)\)")
            if result:
                uvs = [float(c) for c in decode(result[0]).split(" ")]
                face.uv_coords = [[u, v] for u, v in zip(uvs[::2], uvs[1::2])]
                if face.ngons != len(face.uv_coords):
                    raise RuntimeError("Number of UV Coords does not match "
                                       "(expects {}, but {}"
                                       .format(face.ngons,
                                               len(face.uv_coords)))

            result = parse(line, rb"[0-9]+.* COL\(([0-9 ]+)\)")
            if result:
                face.colors = [int(c) for c in result[0].split(" ")]
                if face.ngons != len(face.colors):
                    raise RuntimeError("Number of Colors does not match "
                                       "(expects {}, but {}"
                                       .format(face.ngons, len(face.colors)))

            result = parse(line, rb"[0-9]+.* CRS\(([0-9\. ]+)\)")
            if result:
                face.crs = [float(c) for c in result[0].split(" ")]
                if face.ngons != len(face.crs):
                    raise RuntimeError("Number of CRS does not match "
                                       "(expects {}, but {}"
                                       .format(face.ngons, len(face.crs)))

            faces.append(face)

        raise RuntimeError("Format Error: Failed to parse 'face' field.")

    def _parse_object(self, first_line):
        r = re.compile(rb"Object \"([^\"]+)\" {")
        m = r.search(first_line)
        if not m or len(m.groups()) != 1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

        def parse(l, rgx):
            r = re.compile(rgx)
            m = r.search(l)
            if not m:
                raise RuntimeError("Failed to parse. (line:{})".format(l))
            return m.groups()

        obj = Object()
        obj.name = decode(m.group(1))
        while not self._raw.eof():
            line = self._raw.get_line()
            line = remove_return(line)
            line = line.strip()

            if line.find(b"}") != -1:
                return obj

            if line.find(b"uid ") != -1:
                rgx = rb"uid ([0-9]+)"
                obj.uid = int(parse(line, rgx)[0])
            elif line.find(b"depth ") != -1:
                rgx = rb"depth ([0-9]+)"
                obj.depth = int(parse(line, rgx)[0])
            elif line.find(b"folding ") != -1:
                rgx = rb"folding ([0-1])"
                obj.folding = int(parse(line, rgx)[0])
            elif line.find(b"scale ") != -1:
                rgx = rb"scale ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)"
                obj.scale = [float(v) for v in parse(line, rgx)]
            elif line.find(b"rotation ") != -1:
                rgx = rb"rotation ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)"
                obj.rotation = [float(v) for v in parse(line, rgx)]
            elif line.find(b"translation ") != -1:
                rgx = rb"translation ([-0-9\.]+) ([-0-9\.]+) ([-0-9\.]+)"
                obj.translation = [float(v) for v in parse(line, rgx)]
            elif line.find(b"patch ") != -1:
                rgx = rb"patch ([0-4])"
                obj.patch = int(parse(line, rgx)[0])
            elif line.find(b"patchtri ") != -1:
                rgx = rb"patchtri ([0-1])"
                obj.patch_triangle = int(parse(line, rgx)[0])
            elif line.find(b"segment ") != -1:
                rgx = rb"segment ([0-9]+)"
                obj.segment = int(parse(line, rgx)[0])
            elif line.find(b"visible ") != -1:
                rgx = rb"visible ([0-9]+)"
                obj.visible = int(parse(line, rgx)[0])
            elif line.find(b"locking ") != -1:
                rgx = rb"locking ([0-1])"
                obj.locking = int(parse(line, rgx)[0])
            elif line.find(b"shading ") != -1:
                rgx = rb"shading ([0-1])"
                obj.shading = int(parse(line, rgx)[0])
            elif line.find(b"facet ") != -1:
                rgx = rb"facet ([0-9\.]+)"
                obj.facet = float(parse(line, rgx)[0])
            elif line.find(b"color ") != -1:
                rgx = rb"color ([0-9\.]+) ([0-9\.]+) ([0-9\.]+)"
                obj.color = [float(v) for v in parse(line, rgx)]
            elif line.find(b"color_type ") != -1:
                rgx = rb"color_type ([0-1])"
                obj.color_type = int(parse(line, rgx)[0])
            elif line.find(b"mirror ") != -1:
                rgx = rb"mirror ([0-2])"
                obj.mirror = int(parse(line, rgx)[0])
            elif line.find(b"mirror_axis ") != -1:
                rgx = rb"mirror_axis ([0-4])"
                obj.mirror_axis = int(parse(line, rgx)[0])
            elif line.find(b"mirror_dis ") != -1:
                rgx = rb"mirror_dis ([0-9\.]+)"
                obj.mirror_distance = float(parse(line, rgx)[0])
            elif line.find(b"lathe ") != -1:
                rgx = rb"lathe ([0-3])"
                obj.lathe = int(parse(line, rgx)[0])
            elif line.find(b"lathe_axis ") != -1:
                rgx = rb"lathe_axis ([0-2])"
                obj.lathe_axis = int(parse(line, rgx)[0])
            elif line.find(b"lathe_seg ") != -1:
                rgx = rb"lathe_seg ([0-9]+)"
                obj.lathe_segment = int(parse(line, rgx)[0])
            elif line.find(b"vertex ") != -1:
                obj.add_vertices(self._parse_vertex(line))
            elif line.find(b"BVertex ") != -1:
                raise RuntimeError("BVertex is not supported.")
            elif line.find(b"face ") != -1:
                obj.add_faces(self._parse_face(line))
            elif line.find(b"normal_weight ") != -1:
                rgx = rb"normal_weight ([0-9\.]+)"
                obj.normal_weight = float(parse(line, rgx)[0])
            elif line.find(b"vertexattr ") != -1:
                raise RuntimeError("vertexattr is not supported.")

        raise RuntimeError("Format Error: Failed to parse 'Object' field.")

    def _parse_header(self, line):
        if line != b"Metasequoia Document":
            raise RuntimeError("Header 'Metasequoia Document' is not found.")
        return decode(line)

    def _parse_format_and_version(self, line):
        pattern = rb"Format (Text|Compress) Ver ([0-9]+\.[0-9]+)"
        r = re.compile(pattern)
        m = r.search(line)
        if not m or len(m.groups()) != 2:
            raise RuntimeError("Format/Version is not found.")

        format_ = decode(m.group(1))
        version = float(m.group(2))
        return format_, version

    def _parse_trial_noise(self, first_line):
        if first_line.find(b"TrialNoise") == -1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))

    def _parse_include_xml(self, first_line):
        pattern = rb"IncludeXml \".+\""
        r = re.compile(pattern)
        m = r.search(first_line)
        if not m or len(m.groups()) != 1:
            raise RuntimeError("Invalid format. (line:{})".format(first_line))
        return decode(m.group(1))

    def load(self, filepath):
        with open(filepath, "rb") as f:
            self._raw = RawData(f.read())

        while not self._raw.eof():
            line = self._raw.get_line()
            line = remove_return(line)
            line = line.strip()

            # first line must 'Metasequoia Document'
            if not self._header:
                self._header = self._parse_header(line)
                continue

            # second line must 'Format/Version'
            if not self._format or not self._version:
                self._format, self._version = \
                    self._parse_format_and_version(line)
                continue

            # TODO: parse 'BlackImage' chunk
            # TODO: parse 'Blob' chunk

            if line.find(b"TrialNoise") != -1:
                self._parse_trial_noise(line)
                raise RuntimeError("The file with TrialNoise chuck "
                                   "is not supported.")
            elif line.find(b"IncludeXml") != -1:
                xml_name = self._parse_include_xml(line)
                print(".xml data '{}' will not be loaded.".format(xml_name))
            elif line.find(b"Thumbnail") != -1:
                self._parse_thumbnail(line)
            elif line.find(b"Scene") != -1:
                self._scene = self._parse_scene(line)
            elif line.find(b"Material") != -1:
                self._materials = self._parse_material(line)
            elif line.find(b"Object") != -1:
                self._objects.append(self._parse_object(line))

    def save(self, filepath):
        s = "Metasequoia Document\n"
        s += "Format {} Ver {}\n".format(self._format, self._version)
        s += "\n"

        s += self._scene.to_str(fmt='MQO_FILE')

        if len(self._materials) > 0:
            s += "Material {}".format(len(self._materials)) + " {\n"
            for mtrl in self._materials:
                s += mtrl.to_str(fmt='MQO_FILE')
            s += "}\n"

        for obj in self._objects:
            s += obj.to_str(fmt='MQO_FILE')

        s += "Eof\n\n"

        with open(filepath, "wb") as f:
            f.write(s.encode('UTF-8'))
