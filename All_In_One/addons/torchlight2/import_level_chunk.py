import os
import re
import bpy
import math
import pickle
from mathutils import Vector, Matrix
from collections import deque

from .import_mesh import MeshConverter

RE_FIELD_BEGIN  = re.compile("[ \t]*\[(?P<name>[^/].*?)\]")
RE_FIELD_END    = re.compile("[ \t]*\[/(?P<name>.*?)\]")
RE_FIELD_MEMBER = re.compile("[ \t]*<(?P<type>.*?)>(?P<name>.*?):(?P<value>.*)")

class ParserBase(object):
    def parse(self, filepath):
        regex_to_method = (
            (RE_FIELD_BEGIN,  self.read_field_begin),
            (RE_FIELD_END,    self.read_field_end),
            (RE_FIELD_MEMBER, self.read_field_member)
        )

        with open(filepath, encoding="utf_16_le") as fobj:
            assert fobj.read(1) == "\ufeff"

            for line_nr, line_txt in enumerate(fobj):
                for re, method in regex_to_method:
                    mo = re.match(line_txt)
                    if mo:
                        method(mo, line_nr)
                        break
                else:
                    print("No Match for Line: % 4d" % line_nr)

class DatParser(ParserBase):
    CONVERSIONS = (
        ("BOOL",         bool),
        ("INTEGER",      int),
        ("INTEGER64",    int),
        ("UNSIGNED_INT", int),
        ("FLOAT",        float),
        ("DOUBLE",       float)
    )

    def __init__(self, field_name, cls, filter=None):
        self.field_name = field_name
        self.cls = cls
        self.filter = filter

        self.level = -1
        self.level_active = -1
        self.active = False
        self.current = None

        self.fields = deque()

    def read_field_begin(self, mo, line_nr):
        self.level += 1

        # visiting descendants
        if self.active and self.level > self.level_active:
            self.active = False

        # entering field we search for
        elif mo.group('name') == self.field_name:
            self.active = True
            self.level_active = self.level
            self.current = self.cls()

    def read_field_end(self, mo, line_nr):
        self.level -= 1

        # leaving active field
        if self.active and mo.group('name') == self.field_name:
            self.active = False
            self.level_active = -1
            if self.filter and self.filter(self.current) or not self.filter:
                self.fields.append(self.current)
            self.current = None

        # returning to active field
        elif self.level_active > 0 and self.level == self.level_active:
            self.active = True

    def read_field_member(self, mo, line_nr):
        if self.active:
            (field_type,
             field_name,
             field_value) = mo.groups()

            field_name  = field_name.lower().replace(" ", "_")
            field_value = self.convert(field_type, field_value)

            if field_name not in self.cls.__slots__:
                return

            if field_name not in self.cls._list_members:
                setattr(self.current, field_name, field_value)
            else:
                attr = getattr(self.current, field_name, None)
                if attr is None:
                    setattr(self.current, field_name, field_value)
                elif isinstance(attr, deque):
                    attr.append(field_value)
                else:
                    attr_list = deque()
                    attr_list.append(attr)
                    attr_list.append(field_value)
                    setattr(self.current, field_name, attr_list)

    @classmethod
    def convert(self, field_type, field_value):
        for str_type, py_type in self.CONVERSIONS:
            if str_type == field_type:
                return py_type(field_value)
        else:
            return field_value

    def parse(self, filepath, reset=True):
        ParserBase.parse(self, filepath)
        fields = self.fields
        if reset: self.fields = deque()
        return fields

class Piece(object):
    __slots__ = (
        "name", "guid", "tag", "file", "collisionfile", "fixedvariation",
        "horizontalsnap", "verticalsnap", "rotatesnap", "scalable",
        "rendershadow", "renderorder", "neverbake", "recievespaintedprops"
    )

    _list_members = ("file", "tag")

class PropertiesField(object):
    __slots__ = (
        "descriptor", "name", "parentid", "id",
        "positionx", "positiony", "positionz",
        "forwardx",  "forwardy",  "forwardz",
        "rightx",    "righty",    "rightz",
        "x", "y", "z", "yaw",
        "visible", "layout_file",
        "collision_enabled", "nopath", "guid",
        "active_themes", "deactive_themes"
    )

    _list_members = tuple()

    def __init__(self):
        self.positionx, self.positiony, self.positionz = 0.0, 0.0, 0.0
        self.forwardx,  self.forwardy,  self.forwardz  = 0.0, 0.0, 1.0
        self.rightx,    self.righty,    self.rightz    = 1.0, 0.0, 0.0
        self.x,         self.y,         self.z         = 1.0, 1.0, 1.0

class Theme(object):
    __slots__ = ("theme", "id")
    _list_members = tuple()

def is_room_piece(elem):
    return elem.descriptor == "Room Piece"

def is_group(elem):
    return elem.descriptor == "Group"

def is_layout_link(elem):
    return elem.descriptor == "Layout Link"

def select(elem):
    return elem.descriptor in ("Room Piece", "Group", "Layout Link")

def is_dat_file(f):
    return f.endswith(".DAT")

def build_levelset_dict(tl2_path):
    print("Building Levelset Dictionary")
    levelset_parser = DatParser("PIECE", Piece)
    levelset_dir = os.path.join(tl2_path, "LEVELSETS")
    levelsets = tuple(filter(
        is_dat_file,
        os.listdir(levelset_dir)
        ))

    piece_dict = dict()

    for index, levelset in enumerate(levelsets):
        levelset_path = os.path.join(levelset_dir, levelset)
        pieces = levelset_parser.parse(levelset_path)
        print("Found % 4d pieces in" % len(pieces), levelset)

        for piece in pieces:
            piece_dict[piece.guid] = index

    leveltheme_parser = DatParser("THEME", Theme)
    levelthemes_dir = os.path.join(tl2_path, "LEVELTHEMES")
    themes = tuple(filter(
        is_dat_file,
        os.listdir(levelthemes_dir)
        ))

    theme_dict = dict()

    for theme in themes:
        theme_path = os.path.join(levelthemes_dir, theme)
        leveltheme_parser.parse(theme_path, reset=False)

    for theme in leveltheme_parser.fields:
        theme_dict[theme.id] = theme.theme

    data = {"levelsets": levelsets, "piece_dict": piece_dict, "theme_dict": theme_dict}

    pickle_levelset_dict(data)
    return data

def pickle_levelset_dict(data):
    directory = os.path.dirname(__file__)
    filepath  = os.path.join(directory, "tl2_levelsets.pickle")
    with open(filepath, "wb") as fobj:
        print("Pickling to", filepath)
        pickle.dump(data, fobj, pickle.HIGHEST_PROTOCOL, fix_imports=False)

def cached(func):
    cache = None
    def cached_func():
        nonlocal cache
        if cache is None:
            cache = func()
        return cache
    return cached_func

@cached
def load_levelset_dict():
    directory = os.path.dirname(__file__)
    filepath  = os.path.join(directory, "tl2_levelsets.pickle")
    if os.path.exists(filepath):
        with open(filepath, "rb") as fobj:
            print("Loading Levelsets")
            return pickle.load(fobj)
    else:
        return None

def get_properties_fields(tl2_path, chunk_file, selector):
    chunk_parser = DatParser("PROPERTIES", PropertiesField, selector)
    chunk_path = os.path.join(tl2_path, chunk_file)
    return chunk_parser.parse(chunk_path)

def find_levelset_files(tl2_path, room_pieces, piece_dict, levelsets):
    files = set()
    guids = set()

    for room_piece in room_pieces:
        guid = int(room_piece.guid)
        guids.add(guid)

        try:
            files.add(piece_dict[guid])
        except KeyError:
            print("No piece found for", room_piece.name)
            continue

    files = tuple(os.path.join(tl2_path, "LEVELSETS", levelsets[f]) for f in files)
    return files, guids

def get_matrix_world(elem):
    position = Vector(( elem.positionx, elem.positiony, elem.positionz ))
    forward  = Vector(( elem.forwardx,  elem.forwardy,  elem.forwardz  ))
    right    = Vector(( elem.rightx,    elem.righty,    elem.rightz    ))
    scale    = Vector(( elem.x,         elem.y,         elem.z         ))

    mat_scale = Matrix.Identity(3)
    for i in range(3):
        mat_scale[i][i] = scale[i]

    up = forward.cross(right)
    mat_world = Matrix((right, up, forward))
    mat_world.transpose()
    mat_world = mat_world * mat_scale
    mat_world.resize_4x4()
    mat_world.translation = position

    return mat_world

def strip_media_dir(filepath):
    assert (filepath.startswith("media/") or
            filepath.startswith("MEDIA/"))
    return filepath[6:]

def load_level_chunk(xml_path, tl2_path, chunk_file, parent=None, layout_group=None):
    data = load_levelset_dict() or build_levelset_dict(tl2_path)
    levelsets  = data['levelsets']
    piece_dict = data['piece_dict']
    theme_dict = data['theme_dict']

    fields = get_properties_fields(tl2_path, chunk_file, select)

    room_pieces = tuple(filter(is_room_piece, fields))
    print("\nFound %d room pieces in" % len(room_pieces), os.path.basename(chunk_file))
    files, guids = find_levelset_files(tl2_path, room_pieces, piece_dict, levelsets)

    groups = filter(is_group, fields)
    layout_links = filter(is_layout_link, fields)

    print("Read Room Pieces from", *(os.path.basename(f) for f in files), sep="\n")

    levelset_parser = DatParser("PIECE", Piece, lambda p: p.guid in guids)
    for i, f in enumerate(files):
        levelset_parser.parse(f, reset=False)

    pieces = levelset_parser.fields

    print("%d pieces found" % len(pieces))

    mesh_dict  = dict()
    link_dict  = dict()
    group_dict = dict()
    objects_scene = bpy.context.scene.objects
    objects_data  = bpy.data.objects

    layer_mask_set   = tuple(i == 19 for i in range(20))
    layer_mask_link  = tuple(i == 18 for i in range(20))
    layer_mask_group = tuple(i ==  0 for i in range(20))
    layer_mask_chunk = tuple(i ==  1 for i in range(20))

    print("Create Meshes")

    for i, piece in enumerate(pieces):
        if not hasattr(piece, "file"): continue

        filepath = piece.file if isinstance(piece.file, str) else piece.file[0]
        mesh_input = os.path.join(tl2_path, strip_media_dir(filepath).upper())
        mesh_input = os.path.normpath(mesh_input)
        stem = os.path.basename(mesh_input).rsplit(".")[0]

        mesh_obj  = bpy.data.objects.get(stem)
        mesh_data = bpy.data.meshes.get(stem)

        if not mesh_obj and not mesh_data:
            is_tileset = ( False if not hasattr(piece, "tag") else
                          "TILESET" == piece.tag if isinstance(piece.tag, str) else
                          "TILESET" in piece.tag )

            # if is_tileset:
            #   lvlset_dir = files[piece.tag].rsplit(".")[0]
            #   mat_file = os.path.basename(lvlset_dir) + ".MATERIAL"
            #   mat_input = os.path.join(lvlset_dir, mat_file)
            # else:
            #   mat_input = ""

            try:
                conv = MeshConverter(
                    mesh_input=mesh_input,
                    xml_dir=xml_path,
                    # mat_input=mat_input
                    use_existing_xml=True
                    )
            except FileNotFoundError:
                print(mesh_input, "not found")
                continue

            mesh_obj, mesh_data = conv.create_mesh()
            mesh_obj.layers = layer_mask_set

        mesh_dict[piece.guid] = mesh_data

    print("Create Objects")

    if parent is None:
        stem = os.path.basename(chunk_file).rsplit(".")[0]
        parent = objects_data.new(stem, None)
        objects_scene.link(parent)

        parent.matrix_world = Matrix.Rotation(math.pi / 2.0, 4, 'X')
        parent.layers = layer_mask_group

    for group in groups:
        empty = objects_data.new(group.name, None)
        objects_scene.link(empty)

        group_dict[group.id] = empty
        empty.parent = group_dict.get(group.parentid, parent)
        empty.location = Vector(( group.positionx, group.positiony, group.positionz ))
        empty.layers = (layer_mask_group if not layout_group else
                        layer_mask_link)

        for attr, prefix in zip(("active_themes", "deactive_themes"), ("active_", "inactive_")):
            if hasattr(group, attr):
                themes = getattr(group, attr).strip(" ,").split(",")
                for theme in themes:
                    theme_name = prefix + theme_dict[int(theme)]
                    theme_group = (bpy.data.groups.get(theme_name) or
                                   bpy.data.groups.new(theme_name))

                    theme_group.objects.link(empty)

    for i, room_piece in enumerate(room_pieces):
        mesh = mesh_dict.get(int(room_piece.guid), None)

        obj = objects_data.new(room_piece.name, mesh)
        objects_scene.link(obj)
        obj.layers = (layer_mask_chunk if not layout_group else
                      layer_mask_link)

        obj.matrix_world = get_matrix_world(room_piece)
        obj.parent = group_dict.get(room_piece.parentid, parent)

        if layout_group is not None:
            layout_group.objects.link(obj)

    for layout_link in layout_links:
        layout_link_name = os.path.basename(layout_link.layout_file).rsplit(".")[0]
        data_group = link_dict.get(layout_link.layout_file)

        if data_group is None:
            data_group = bpy.data.groups.new(layout_link_name)
            link_dict[layout_link.layout_file] = data_group

            layout_link_parent = objects_data.new(layout_link_name, None)
            objects_scene.link(layout_link_parent)
            data_group.objects.link(layout_link_parent)
            layout_link_parent.layers = layer_mask_link

            load_level_chunk(
                xml_path,
                tl2_path,
                strip_media_dir(layout_link.layout_file),
                layout_link_parent,
                data_group
            )

        layout_link_instance = objects_data.new(layout_link.name, None)
        objects_scene.link(layout_link_instance)

        layout_link_instance.matrix_world = get_matrix_world(layout_link)
        layout_link_instance.parent = group_dict.get(layout_link.parentid, parent)
        layout_link_instance.layers = (layer_mask_chunk if not layout_group else
                                       layer_mask_link)

        layout_link_instance.dupli_type = "GROUP"
        layout_link_instance.dupli_group = data_group
