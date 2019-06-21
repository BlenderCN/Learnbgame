"""This module provides file I/O for Quake 2 BSP map files.

Example:
    bsp_file = bsp.Bsp.open('base1.bsp')

References:
    Quake 2 Source
    - id Software
    - https://github.com/id-Software/Quake-2

    Quake 2 BSP File Format
    - Max McGuire
    - http://www.flipcode.com/archives/Quake_2_BSP_File_Format.shtml
"""

import io
import struct

__all__ = ['BadBspFile', 'is_bspfile', 'Bsp']


class BadBspFile(Exception):
    pass


def _check_bspfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<4si'))
    identity, version = struct.unpack('<4si', data)[0]

    return identity is b'IBSP' and version is 38


def is_bspfile(filename):
    """Quickly see if a file is a bsp file by checking the magic number.

    The filename argument may be a file for file-like object.
    """
    result = False

    try:
        if hasattr(filename, 'read'):
            return _check_bspfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_bspfile(fp)

    except:
        pass

    return result


class ClassSequence:
    """Class for reading a sequence of data structures"""
    Class = None

    @classmethod
    def write(cls, file, structures):
        for structure in structures:
            cls.Class.write(file, structure)

    @classmethod
    def read(cls, file):
        return [cls.Class(*c) for c in struct.iter_unpack(cls.Class.format, file.read())]


class Entities:
    """Class for representing the entities lump"""
    @classmethod
    def write(cls, file, entities):
        entities_data = entities.encode('cp437')
        file.write(entities_data)

    @classmethod
    def read(cls, file):
        entities_data = file.read()
        return entities_data.decode('cp437')


class Plane:
    """Class for representing a bsp plane

    Attributes:
        normal: The normal vector to the plane.

        distance: The distance from world (0, 0, 0) to a point on the plane

        type: Planes are classified as follows:
            0: Axial plane aligned to the x-axis.
            1: Axial plane aligned to the y-axis.
            2: Axial plane aligned to the z-axis.
            3: Non-axial plane roughly aligned to the x-axis.
            4: Non-axial plane roughly aligned to the y-axis.
            5: Non-axial plane roughly aligned to the z-axis.
    """

    format = '<4fi'
    size = struct.calcsize(format)

    __slots__ = (
        'normal',
        'distance',
        'type'
    )

    def __init__(self,
                 normal_x,
                 normal_y,
                 normal_z,
                 distance,
                 type):

        self.normal = normal_x, normal_y, normal_z
        self.distance = distance
        self.type = type

    @classmethod
    def write(cls, file, plane):
        plane_data = struct.pack(cls.format,
                                 *plane.normal,
                                 plane.distance,
                                 plane.type)

        file.write(plane_data)

    @classmethod
    def read(cls, file):
        plane_data = file.read(cls.size)
        plane_struct = struct.unpack(cls.format, plane_data)

        return Plane(*plane_struct)


class Planes(ClassSequence):
    Class = Plane


class Vertex:
    """Class for representing a vertex

    A Vertex is an XYZ triple.

    Attributes:
        x: The x-coordinate

        y: The y-coordinate

        z: The z-coordinate
    """

    format = '<3f'
    size = struct.calcsize(format)

    __slots__ = (
        'x',
        'y',
        'z'
    )

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __getitem__(self, item):
        if type(item) is int:
            return [self.x, self.y, self.z][item]

        elif type(item) is slice:
            start = item.start or 0
            stop = item.stop or 3

            return [self.x, self.y, self.z][start:stop]

    @classmethod
    def write(cls, file, vertex):
        vertex_data = struct.pack(cls.format,
                                  vertex.x,
                                  vertex.y,
                                  vertex.z)

        file.write(vertex_data)

    @classmethod
    def read(cls, file):
        vertex_data = file.read(cls.size)
        vertex_struct = struct.unpack(cls.format, vertex_data)

        return Vertex(*vertex_struct)


class Vertexes(ClassSequence):
    Class = Vertex


class Visibilities:
    @classmethod
    def write(cls, file, structures):
        file.write(structures)

    @classmethod
    def read(cls, file):
        return file.read()


class Node:
    """Class for representing a node

    A Node is a data structure used to compose a bsp tree data structure. A
    child may be a Node or a Leaf.

    Attributes:
        plane_number: The number of the plane that partitions the node.

        children: A two-tuple of the two sub-spaces formed by the partitioning
            plane.

            Note: Child 0 is the front sub-space, and 1 is the back sub-space.

            Note: If bit 15 is set, the child is a leaf.

        bounding_box_min: The minimum coordinate of the bounding box containing
            this node and all of its children.

        bounding_box_max: The maximum coordinate of the bounding box containing
            this node and all of its children.

        first_face: The number of the first face in Bsp.mark_surfaces.

        number_of_faces: The number of faces contained in the node. These
            are stored in consecutive order in Bsp.mark_surfaces starting at
            Node.first_face.
    """

    format = '<3i6h2H'
    size = struct.calcsize(format)

    __slots__ = (
        'plane_number',
        'children',
        'bounding_box_min',
        'bounding_box_max',
        'first_face',
        'number_of_faces'
    )

    def __init__(self,
                 plane_number,
                 child_front,
                 child_back,
                 bounding_box_min_x,
                 bounding_box_min_y,
                 bounding_box_min_z,
                 bounding_box_max_x,
                 bounding_box_max_y,
                 bounding_box_max_z,
                 first_face,
                 number_of_faces):

        self.plane_number = plane_number
        self.children = child_front, child_back
        self.bounding_box_min = bounding_box_min_x, bounding_box_min_y, bounding_box_min_z
        self.bounding_box_max = bounding_box_max_x, bounding_box_max_y, bounding_box_max_z
        self.first_face = first_face
        self.number_of_faces = number_of_faces

    @classmethod
    def write(cls, file, node):
        node_data = struct.pack(cls.format,
                                node.plane_number,
                                *node.children,
                                *node.bounding_box_min,
                                *node.bounding_box_max,
                                node.first_face,
                                node.number_of_faces)

        file.write(node_data)

    @classmethod
    def read(cls, file):
        node_data = file.read(cls.size)
        node_struct = struct.unpack(cls.format, node_data)

        return Node(*node_struct)


class Nodes(ClassSequence):
    Class = Node


class SurfaceFlag:
    LIGHT = 0x1
    SLICK = 0x2
    SKY = 0x4
    WARP = 0x8
    TRANS33 = 0x10
    TRANS66 = 0x20
    FLOWING = 0x40
    NODRAW = 0x80


class TextureInfo:
    """Class for representing a texture info

    Attributes:
        s: The s vector in texture space represented as an XYZ three-tuple.

        s_offset: Horizontal offset in texture space.

        t: The t vector in texture space represented as an XYZ three-tuple.

        t_offset: Vertical offset in texture space.

        flags: A bitfield of surface behaviors.

        value:

        texture_name: The path of the texture.

        next_texture_info: For animated textures. Sequence will be terminated
            with a value of -1

    """

    format = '<8f2i32si'
    size = struct.calcsize(format)

    __slots__ = (
        's',
        's_offset',
        't',
        't_offset',
        'flags',
        'value',
        'texture_name',
        'next_texture_info'
    )

    def __init__(self,
                 s_x,
                 s_y,
                 s_z,
                 s_offset,
                 t_x,
                 t_y,
                 t_z,
                 t_offset,
                 flags,
                 value,
                 texture_name,
                 next_texture_info):

        self.s = s_x, s_y, s_z
        self.s_offset = s_offset
        self.t = t_x, t_y, t_z
        self.t_offset = t_offset
        self.flags = flags
        self.value = value

        if type(texture_name) == bytes:
            self.texture_name = texture_name.split(b'\00')[0].decode('ascii')
        else:
            self.texture_name = texture_name

        self.next_texture_info = next_texture_info

    @classmethod
    def write(cls, file, texture_info):
        texture_info_data = struct.pack(cls.format,
                                        *texture_info.s,
                                        texture_info.s_offset,
                                        *texture_info.t,
                                        texture_info.t_offset,
                                        texture_info.flags,
                                        texture_info.value,
                                        texture_info.texture_name.encode('ascii'),
                                        texture_info.next_texture_info)
        file.write(texture_info_data)

    @classmethod
    def read(cls, file):
        texture_info_data = file.read(cls.size)
        texture_info_struct = struct.unpack(cls.format, texture_info_data)

        return TextureInfo(*texture_info_struct)


class TextureInfos(ClassSequence):
    Class = TextureInfo


class Face:
    """Class for representing a face

    Attributes:
        plane_number: The plane in which the face lies.

        side: Which side of the plane the face lies. 0 is the front, 1 is the
            back.

        first_edge: The number of the first edge in Bsp.surf_edges.

        number_of_edges: The number of edges contained within the face. These
            are stored in consecutive order in Bsp.surf_edges starting at
            Face.first_edge.

        texture_info: The number of the texture info for this face.

        styles: A four-tuple of lightmap styles.

        light_offset: The offset into the lighting data.
    """

    format = '<Hhi2h4Bi'
    size = struct.calcsize(format)

    __slots__ = (
        'plane_number',
        'side',
        'first_edge',
        'number_of_edges',
        'texture_info',
        'styles',
        'light_offset'
    )

    def __init__(self,
                 plane_number,
                 side,
                 first_edge,
                 number_of_edges,
                 texture_info,
                 style_0,
                 style_1,
                 style_2,
                 style_3,
                 light_offset):

        self.plane_number = plane_number
        self.side = side
        self.first_edge = first_edge
        self.number_of_edges = number_of_edges
        self.texture_info = texture_info
        self.styles = style_0, style_1, style_2, style_3
        self.light_offset = light_offset

    @classmethod
    def write(cls, file, plane):
        face_data = struct.pack(cls.format,
                                plane.plane_number,
                                plane.side,
                                plane.first_edge,
                                plane.number_of_edges,
                                plane.texture_info,
                                *plane.styles,
                                plane.light_offset)

        file.write(face_data)

    @classmethod
    def read(cls, file):
        face_data = file.read(cls.size)
        face_struct = struct.unpack(cls.format, face_data)

        return Face(*face_struct)


class Faces(ClassSequence):
    Class = Face


class Lighting:
    @classmethod
    def write(cls, file, lighting):
        file.write(lighting)

    @classmethod
    def read(cls, file):
        return file.read()


class Contents:
    SOLID = 1
    WINDOW = 2
    AUX = 4
    LAVA = 8
    SLIME = 16
    WATER = 32
    MIST = 64
    LAST_VISIBLE = 64
    AREAPORTAL = 0x8000
    PLAYERCLIP = 0x10000
    MONSTERCLIP = 0x20000
    CURRENT_0 = 0x40000
    CURRENT_90 = 0x80000
    CURRENT_180 = 0x100000
    CURRENT_270 = 0x200000
    CURRENT_UP = 0x400000
    CURRENT_DOWN = 0x800000
    ORIGIN = 0x1000000
    MONSTER = 0x2000000
    DEADMONSTER = 0x4000000
    DETAIL = 0x8000000
    TRANSLUCENT = 0x10000000
    LADDER = 0x20000000


class Leaf:
    """Class for representing a leaf

    Attributes:
        contents: The content of the leaf. Affect the player's view.

        cluster: The cluster containing this leaf. -1 for no visibility info.

        area: The area containing this leaf.

        bounding_box_min: The minimum coordinate of the bounding box containing
            this node.

        bounding_box_max: The maximum coordinate of the bounding box containing
            this node.

        first_leaf_face: The number of the first face in Bsp.faces

        number_of_leaf_faces: The number of faces contained within the leaf.
            These are stored in consecutive order in Bsp.faces at
            Leaf.first_leaf_face.

        first_leaf_brush: The number of the first brush in Bsp.brushes

        number_of_leaf_brushes: The number of brushes contained within the
            leaf. These are stored in consecutive order in Bsp.brushes at
            Leaf.first_leaf_brush.
    """

    format = '<i8h4H'
    size = struct.calcsize(format)

    __slots__ = (
        'contents',
        'cluster',
        'area',
        'bounding_box_min',
        'bounding_box_max',
        'first_leaf_face',
        'number_of_leaf_faces',
        'first_leaf_brush',
        'number_of_leaf_brushes'
    )

    def __init__(self,
                 contents,
                 cluster,
                 area,
                 bounding_box_min_x,
                 bounding_box_min_y,
                 bounding_box_min_z,
                 bounding_box_max_x,
                 bounding_box_max_y,
                 bounding_box_max_z,
                 first_leaf_face,
                 number_of_leaf_faces,
                 first_leaf_brush,
                 number_of_leaf_brushes):

        self.contents = contents
        self.cluster = cluster
        self.area = area
        self.bounding_box_min = bounding_box_min_x, bounding_box_min_y, bounding_box_min_z
        self.bounding_box_max = bounding_box_max_x, bounding_box_max_y, bounding_box_max_z
        self.first_leaf_face = first_leaf_face
        self.number_of_leaf_faces = number_of_leaf_faces
        self.first_leaf_brush = first_leaf_brush
        self.number_of_leaf_brushes = number_of_leaf_brushes

    @classmethod
    def write(cls, file, leaf):
        leaf_data = struct.pack(cls.format,
                                leaf.contents,
                                leaf.cluster,
                                leaf.area,
                                *leaf.bounding_box_min,
                                *leaf.bounding_box_max,
                                leaf.first_leaf_face,
                                leaf.number_of_leaf_faces,
                                leaf.first_leaf_brush,
                                leaf.number_of_leaf_brushes)

        file.write(leaf_data)

    @classmethod
    def read(cls, file):
        leaf_data = file.read(cls.size)
        leaf_struct = struct.unpack(cls.format, leaf_data)

        return Leaf(*leaf_struct)


class Leafs(ClassSequence):
    Class = Leaf


class LeafFaces:
    @classmethod
    def write(cls, file, leaf_faces):
        leaf_faces_format = '<{}H'.format(len(leaf_faces))
        leaf_faces_data = struct.pack(leaf_faces_format, *leaf_faces)

        file.write(leaf_faces_data)

    @classmethod
    def read(cls, file):
        return [lf[0] for lf in struct.iter_unpack('<H', file.read())]


class LeafBrushes:
    @classmethod
    def write(cls, file, leaf_brushes):
        leaf_brushes_format = '<{}H'.format(len(leaf_brushes))
        leaf_brushes_data = struct.pack(leaf_brushes_format, *leaf_brushes)

        file.write(leaf_brushes_data)

    @classmethod
    def read(cls, file):
        return [lb[0] for lb in struct.iter_unpack('<H', file.read())]


class Edge:
    """Class for representing a edge

    Attributes:
        vertexes: A two-tuple of vertexes that form the edge. Vertex 0 is the
            start vertex, and 1 is the end vertex.
    """

    format = '<2H'
    size = struct.calcsize(format)

    __slots__ = (
        'vertexes'
    )

    def __init__(self, vertex_0, vertex_1):
        self.vertexes = vertex_0, vertex_1

    def __getitem__(self, item):
        if item > 1:
            raise IndexError('list index of out of range')

        return self.vertexes[item]

    @classmethod
    def write(cls, file, edge):
        edge_data = struct.pack(cls.format,
                                *edge.vertexes)

        file.write(edge_data)

    @classmethod
    def read(cls, file):
        edge_data = file.read(cls.size)
        edge_struct = struct.unpack(cls.format, edge_data)

        return Edge(*edge_struct)


class Edges(ClassSequence):
    Class = Edge


class SurfEdges:
    @classmethod
    def write(cls, file, surf_edges):
        surf_edges_format = '<{}H'.format(len(surf_edges))
        surf_edges_data = struct.pack(surf_edges_format, *surf_edges)

        file.write(surf_edges_data)

    @classmethod
    def read(cls, file):
        return [se[0] for se in struct.iter_unpack('<H', file.read())]


class Model:
    """Class for representing a model

    Attributes:
        bounding_box_min: The minimum coordinate of the bounding box containing
            the model.

        bounding_box_max: The maximum coordinate of the bounding box containing
            the model.

        origin: The origin of the model.

        head_node: A four-tuple of indexes. Corresponds to number of map hulls.

        visleafs: The number of leaves in the bsp tree?

        first_face: The number of the first face in Bsp.mark_surfaces.

        number_of_faces: The number of faces contained in the node. These
            are stored in consecutive order in Bsp.mark_surfaces starting at
            Model.first_face.
    """

    format = '<9f3i'
    size = struct.calcsize(format)

    __slots__ = (
        'bounding_box_min',
        'bounding_box_max',
        'origin',
        'head_node',
        'first_face',
        'number_of_faces'
    )

    def __init__(self,
                 bounding_box_min_x,
                 bounding_box_min_y,
                 bounding_box_min_z,
                 bounding_box_max_x,
                 bounding_box_max_y,
                 bounding_box_max_z,
                 origin_x,
                 origin_y,
                 origin_z,
                 head_node,
                 first_face,
                 number_of_faces):

        self.bounding_box_min = bounding_box_min_x, bounding_box_min_y, bounding_box_min_z
        self.bounding_box_max = bounding_box_max_x, bounding_box_max_y, bounding_box_max_z
        self.origin = origin_x, origin_y, origin_z
        self.head_node = head_node
        self.first_face = first_face
        self.number_of_faces = number_of_faces

    @classmethod
    def write(cls, file, model):
        model_data = struct.pack(cls.format,
                                 *model.bounding_box_min,
                                 *model.bounding_box_max,
                                 *model.origin,
                                 model.head_node,
                                 model.first_face,
                                 model.number_of_faces)

        file.write(model_data)

    @classmethod
    def read(cls, file):
        model_data = file.read(cls.size)
        model_struct = struct.unpack(cls.format, model_data)

        return Model(*model_struct)


class Models(ClassSequence):
    Class = Model


class Brush:
    format = '<3i'
    size = struct.calcsize(format)

    __slots__ = (
        'first_side',
        'number_of_sides',
        'contents'
    )

    def __init__(self,
                 first_side,
                 number_of_sides,
                 contents):

        self.first_side = first_side
        self.number_of_sides = number_of_sides
        self.contents = contents

    @classmethod
    def write(cls, file, brush):
        brush_data = struct.pack(cls.format,
                                 brush.first_side,
                                 brush.number_of_sides,
                                 brush.contents)

        file.write(brush_data)

    @classmethod
    def read(cls, file):
        brush_data = file.read(cls.size)
        brush_struct = struct.unpack(cls.format, brush_data)

        return Brush(*brush_struct)


class Brushes(ClassSequence):
    Class = Brush


class BrushSide:
    format = '<Hh'
    size = struct.calcsize(format)

    __slots__ = (
        'plane_number',
        'texture_info'
    )

    def __init__(self,
                 plane_number,
                 texture_info):

        self.plane_number = plane_number
        self.texture_info = texture_info

    @classmethod
    def write(cls, file, brush_side):
        brush_side_data = struct.pack(cls.format,
                                      brush_side.plane_number,
                                      brush_side.texture_info)

        file.write(brush_side_data)

    @classmethod
    def read(cls, file):
        brush_side_data = file.read(cls.size)
        brush_side_struct = struct.unpack(cls.format, brush_side_data)

        return BrushSide(*brush_side_struct)


class BrushSides(ClassSequence):
    Class = BrushSide


class Pop:
    @classmethod
    def write(cls, file, structures):
        file.write(structures)

    @classmethod
    def read(cls, file):
        return file.read()


class Area:
    format = '<2i'
    size = struct.calcsize(format)

    __slots__ = (
        'number_of_area_portals',
        'first_area_portal'
    )

    def __init__(self,
                 number_of_area_portals,
                 first_area_portal):

        self.number_of_area_portals = number_of_area_portals
        self.first_area_portal = first_area_portal

    @classmethod
    def write(cls, file, area):
        area_data = struct.pack(cls.format,
                                area.number_of_area_portals,
                                area.first_area_portal)

        file.write(area_data)

    @classmethod
    def read(cls, file):
        area_data = file.read(cls.size)
        area_struct = struct.unpack(cls.format, area_data)

        return Area(*area_struct)


class Areas(ClassSequence):
    Class = Area


class AreaPortal:
    format = '<2i'
    size = struct.calcsize(format)

    __slots__ = (
        'portal_number',
        'other_area'
    )

    def __init__(self,
                 portal_number,
                 other_area):
        self.portal_number = portal_number
        self.other_area = other_area

    @classmethod
    def write(cls, file, area):
        area_data = struct.pack(cls.format,
                                area.portal_number,
                                area.other_area)

        file.write(area_data)

    @classmethod
    def read(cls, file):
        area_data = file.read(cls.size)
        area_struct = struct.unpack(cls.format, area_data)

        return AreaPortal(*area_struct)


class AreaPortals(ClassSequence):
    Class = AreaPortal


class Lump:
    """Class for representing a lump.

    A lump is a section of data that typically contains a sequence of data
    structures.

    Attributes:
        offset: The offset of the lump entry from the start of the file.

        length: The length of the lump entry.
    """

    format = '<2i'
    size = struct.calcsize(format)

    __slots__ = (
        'offset',
        'length'
    )

    def __init__(self, offset, length):
        self.offset = offset
        self.length = length

    @classmethod
    def write(cls, file, lump):
        lump_data = struct.pack(cls.format,
                                lump.offset,
                                lump.length)

        file.write(lump_data)

    @classmethod
    def read(cls, file):
        lump_data = file.read(cls.size)
        lump_struct = struct.unpack(cls.format, lump_data)

        return Lump(*lump_struct)


class Header:
    """Class for representing a Bsp file header

    Attributes:
        identity: The file identity. Should be b'IBSP'.

        version: The file version. Should be 38.

        lumps: A sequence of nineteen Lumps
    """

    format = '<4si{}'.format(Lump.format[1:] * 19)
    size = struct.calcsize(format)
    order = [
        Entities,
        Planes,
        Vertexes,
        Visibilities,
        Nodes,
        TextureInfos,
        Faces,
        Lighting,
        Leafs,
        LeafFaces,
        LeafBrushes,
        Edges,
        SurfEdges,
        Models,
        Brushes,
        BrushSides,
        Pop,
        Areas,
        AreaPortals
    ]

    __slots__ = (
        'identity',
        'version',
        'lumps'
    )

    def __init__(self,
                 identity,
                 version,
                 lumps):

        self.identity = identity
        self.version = version
        self.lumps = lumps

    @classmethod
    def write(cls, file, header):
        lump_values = []
        for lump in header.lumps:
            lump_values += lump.offset, lump.length

        header_data = struct.pack(cls.format,
                                  header.identity,
                                  header.version,
                                  *lump_values)

        file.write(header_data)

    @classmethod
    def read(cls, file):
        data = file.read(cls.size)
        lumps_start = struct.calcsize('<4si')

        header_data = data[:lumps_start]
        header_struct = struct.unpack('<4si', header_data)
        ident = header_struct[0]
        version = header_struct[1]

        lumps_data = data[lumps_start:]
        lumps = [Lump(*l) for l in struct.iter_unpack(Lump.format, lumps_data)]

        return Header(ident, version, lumps)


class Bsp:
    """Class for working with Bsp files

    Example:
        b = Bsp.open(file)

    Attributes:
        identity: Identity of the Bsp file. Should be b'IBSP'

        version: Version of the Bsp file. Should be 38

        entities: A string containing the entity definitions.

        planes: A list of Plane objects used by the bsp tree data structure.

        vertexes: A list of Vertex objects.

        visibilities: A list of integers representing visibility data.

        nodes: A list of Node objects used by the bsp tree data structure.

        texture_infos: A list of TextureInfo objects.

        faces: A list of Face objects.

        lighting: A list of ints representing lighting data.

        leafs: A list of Leaf objects used by the bsp tree data structure.

        leaf_faces: A list of ints representing a consecutive list of faces
            used by the Leaf objects.

        leaf_brushes: A list of ints representing a consecutive list of edges
            used by the Leaf objects.

        edges: A list of Edge objects.

        surf_edges: A list of ints representing a consecutive list of edges
            used by the Face objects.

        models: A list of Model objects.

        brushes: A list of Brush objects.

        brush_sides: A list of BrushSide objects.

        pop: Proof of purchase? Always 256 bytes of null data if present.

        areas: A list of Area objects.

        area_portals: A list of AreaPortal objects.
    """

    def __init__(self):
        self.fp = None
        self.mode = None
        self._did_modify = False

        self.identity = b'IBSP'
        self.version = 38
        self.entities = ""
        self.planes = []
        self.vertexes = []
        self.visibilities = []
        self.nodes = []
        self.texture_infos = []
        self.faces = []
        self.lighting = b''
        self.leafs = []
        self.leaf_faces = []
        self.leaf_brushes = []
        self.edges = []
        self.surf_edges = []
        self.models = []
        self.brushes = []
        self.brush_sides = []
        self.pop = []
        self.areas = []
        self.area_portals = []

    Lump = Lump
    Header = Header
    Entities = Entities
    Planes = Planes
    Vertexes = Vertexes
    Visibilities = Visibilities
    Visibilities = Visibilities
    Nodes = Nodes
    TextureInfos = TextureInfos
    Faces = Faces
    Lighting = Lighting
    Leafs = Leafs
    LeafFaces = LeafFaces
    LeafBrushes = LeafBrushes
    Edges = Edges
    SurfEdges = SurfEdges
    Models = Models
    Brushes = Brushes
    BrushSides = BrushSides
    Pop = Pop
    Areas = Areas
    AreaPortals = AreaPortals

    @classmethod
    def open(cls, file, mode='r'):
        """Returns a Bsp object

        Args:
            file: Either the path to the file, a file-like object, or bytes.

            mode: An optional string that indicates which mode to open the file

        Returns:
            An Bsp object constructed from the information read from the
            file-like object.

        Raises:
            ValueError: If an invalid file mode is given.

            RuntimeError: If the file argument is not a file-like object.
        """

        if mode not in ('r', 'w', 'a'):
            raise ValueError("invalid mode: '%s'" % mode)

        filemode = {'r': 'rb', 'w': 'w+b', 'a': 'r+b'}[mode]

        if isinstance(file, str):
            file = io.open(file, filemode)

        elif isinstance(file, bytes):
            file = io.BytesIO(file)

        elif not hasattr(file, 'read'):
            raise RuntimeError(
                "Bsp.open() requires 'file' to be a path, a file-like object, "
                "or bytes")

        # Read
        if mode == 'r':
            return cls._read_file(file, mode)

        # Write
        elif mode == 'w':
            bsp = cls()
            bsp.fp = file
            bsp.mode = 'w'
            bsp._did_modify = True

            return bsp

        # Append
        else:
            bsp = cls._read_file(file, mode)
            bsp._did_modify = True

            return bsp

    @classmethod
    def _read_file(cls, file, mode):
        def _read_lump(Class):
            lump = header.lumps[header.order.index(Class)]
            file.seek(lump.offset)

            return Class.read(io.BytesIO(file.read(lump.length)))

        bsp = cls()
        bsp.mode = mode
        bsp.fp = file

        # Header
        header = cls.Header.read(file)
        bsp.identity = header.identity
        bsp.version = header.version

        bsp.entities = _read_lump(cls.Entities)
        bsp.planes = _read_lump(cls.Planes)
        bsp.vertexes = _read_lump(cls.Vertexes)
        bsp.visibilities = _read_lump(cls.Visibilities)
        bsp.nodes = _read_lump(cls.Nodes)
        bsp.texture_infos = _read_lump(cls.TextureInfos)
        bsp.faces = _read_lump(cls.Faces)
        bsp.lighting = _read_lump(cls.Lighting)
        bsp.leafs = _read_lump(cls.Leafs)
        bsp.leaf_faces = _read_lump(cls.LeafFaces)
        bsp.leaf_brushes = _read_lump(cls.LeafBrushes)
        bsp.edges = _read_lump(cls.Edges)
        bsp.surf_edges = _read_lump(cls.SurfEdges)
        bsp.models = _read_lump(cls.Models)
        bsp.brushes = _read_lump(cls.Brushes)
        bsp.brush_sides = _read_lump(cls.BrushSides)
        bsp.pop = _read_lump(cls.Pop)
        bsp.areas = _read_lump(cls.Areas)
        bsp.area_portals = _read_lump(cls.AreaPortals)

        return bsp

    @classmethod
    def _write_file(cls, file, bsp):
        def _write_lump(Class, data):
            offset = file.tell()
            Class.write(file, data)
            size = file.tell() - offset

            return cls.Lump(offset, size)

        lumps = [cls.Lump(0, 0) for _ in range(19)]
        header = cls.Header(bsp.identity, bsp.version, lumps)
        lump_index = header.order.index

        # Stub out header info
        cls.Header.write(file, header)

        lumps[lump_index(cls.Entities)] = _write_lump(cls.Entities, bsp.entities)
        lumps[lump_index(cls.Planes)] = _write_lump(cls.Planes, bsp.planes)
        lumps[lump_index(cls.Vertexes)] = _write_lump(cls.Vertexes, bsp.vertexes)
        lumps[lump_index(cls.Visibilities)] = _write_lump(cls.Visibilities, bsp.visibilities)
        lumps[lump_index(cls.Nodes)] = _write_lump(cls.Nodes, bsp.nodes)
        lumps[lump_index(cls.TextureInfos)] = _write_lump(cls.TextureInfos, bsp.texture_infos)
        lumps[lump_index(cls.Faces)] = _write_lump(cls.Faces, bsp.faces)
        lumps[lump_index(cls.Lighting)] = _write_lump(cls.Lighting, bsp.lighting)
        lumps[lump_index(cls.Leafs)] = _write_lump(cls.Leafs, bsp.leafs)
        lumps[lump_index(cls.LeafFaces)] = _write_lump(cls.LeafFaces, bsp.leaf_faces)
        lumps[lump_index(cls.LeafBrushes)] = _write_lump(cls.LeafBrushes, bsp.leaf_brushes)
        lumps[lump_index(cls.Edges)] = _write_lump(cls.Edges, bsp.edges)
        lumps[lump_index(cls.SurfEdges)] = _write_lump(cls.SurfEdges, bsp.surf_edges)
        lumps[lump_index(cls.Models)] = _write_lump(cls.Models, bsp.models)
        lumps[lump_index(cls.Brushes)] = _write_lump(cls.Brushes, bsp.brushes)
        lumps[lump_index(cls.BrushSides)] = _write_lump(cls.BrushSides, bsp.brush_sides)
        lumps[lump_index(cls.Pop)] = _write_lump(cls.Pop, bsp.pop)
        lumps[lump_index(cls.Areas)] = _write_lump(cls.Areas, bsp.areas)
        lumps[lump_index(cls.AreaPortals)] = _write_lump(cls.AreaPortals, bsp.area_portals)

        end_of_file = file.tell()

        # Finalize header
        file.seek(0)
        cls.Header.write(file, header)
        file.seek(end_of_file)

    def save(self, file):
        """Writes Bsp data to file

        Args:
            file: Either the path to the file, or a file-like object, or bytes.

        Raises:
            RuntimeError: If the file argument is not a file-like object.
        """

        should_close = False

        if isinstance(file, str):
            file = io.open(file, 'r+b')
            should_close = True

        elif isinstance(file, bytes):
            file = io.BytesIO(file)
            should_close = True

        elif not hasattr(file, 'write'):
            raise RuntimeError(
                "Bsp.open() requires 'file' to be a path, a file-like object, "
                "or bytes")

        self._write_file(file, self)

        if should_close:
            file.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        """Closes the file pointer if possible. If mode is 'w' or 'a', the file
        will be written to.
        """

        if self.fp:
            if self.mode in ('w', 'a') and self._did_modify:
                self.fp.seek(0)
                self._write_file(self.fp, self)
                self.fp.truncate()

            file_object = self.fp
            self.fp = None
            file_object.close()
