""" This files contains classes that interpret the .egg object model and write
out the appropriate Blender structures. """

from .eggparser import parse_egg, parse_number

import sys, os
import bpy
import io, zlib
from mathutils import Matrix, Vector
from math import radians

DEFAULT_UV_NAME = "UVMap"


class EggContext:

    # These matrices are used for coordinate system conversion.
    y_to_z_up_mat = Matrix(((1.0, 0.0, 0.0, 0.0),
                            (0.0, 0.0, 1.0, 0.0),
                            (0.0,-1.0, 0.0, 0.0),
                            (0.0, 0.0, 0.0, 1.0)))

    flip_y_mat = Matrix(((1.0, 0.0, 0.0, 0.0),
                         (0.0,-1.0, 0.0, 0.0),
                         (0.0, 0.0, 1.0, 0.0),
                         (0.0, 0.0, 0.0, 1.0)))

    def __init__(self):
        self.vertex_pools = {}
        self.materials = {}
        self.textures = {}
        self.search_dir = None

        self.duplicate_faces = 0
        self.degenerate_faces = 0

        # For presumably historical reasons, .egg defaults to Y-Up-Right.
        self.coord_system = None
        self.up_vector = Vector((0, 0, 0))
        self.right_vector = Vector((1, 0, 0))
        self.forward_vector = Vector((0, 0, 0))
        self.cs_matrix = self.y_to_z_up_mat
        self.inv_cs_matrix = self.y_to_z_up_mat.inverted()

        # Remember external references.
        self.external_groups = {}

        # We remember all the Group/VertexRef entries, so we can assign them
        # in a separate pass.
        self.group_vertex_refs = []

        self.joints = {}

    def read_file(self, path):
        """ Reads an .egg file, returning a root EggGroupNode. """

        if path.endswith('.pz') or path.endswith('.gz'):
            data = zlib.decompress(open(path, 'rb').read(), 32 + 15).decode('utf-8')
        elif not os.path.isfile(path) and not os.path.splitext(path)[1]:
            # Implicit .egg extension.
            data = open(path + '.egg', 'r').read()
        else:
            data = open(path, 'r').read()

        buffer = io.StringIO(data)
        root = EggGroupNode()
        parse_egg(buffer, root, self)
        buffer.close()

        return root

    def info(self, message):
        """ Called when the importer wants to report something.  This can be
        overridden to do something useful, such as report to the user. """
        pass

    def warn(self, message):
        """ Called when the importer wants to warn about something.  This can
        be overridden to do something useful, such as report to the user. """
        pass

    def error(self, message):
        """ Called when the importer wants to error about something.  This can
        be overridden to do something useful, such as report to the user. """
        pass

    def set_coordinate_system(self, coordsys):
        """ Called when a <CoordinateSystem> entry is encountered in the .egg
        file.  This can occur anywhere in the .egg file, but there may not be
        two mismatching entries. """

        # Canonicalise coordinate system value.
        canonical = coordsys.strip().upper().replace('-', '').replace('_', '').replace('RIGHT', '')

        if canonical == 'ZUP':
            self.cs_matrix = Matrix.Identity(4)
            self.up_vector = Vector((0, 0, 1))
            self.forward_vector = Vector((0, 1, 0))
        elif canonical == 'YUP':
            self.cs_matrix = self.y_to_z_up_mat
            self.up_vector = Vector((0, 1, 0))
            self.forward_vector = Vector((0, 0, -1))
        elif canonical == 'ZUPLEFT':
            self.cs_matrix = self.flip_y_mat
            self.up_vector = Vector((0, 0, 1))
            self.forward_vector = Vector((0, -1, 0))
        elif canonical == 'YUPLEFT':
            self.cs_matrix = self.y_to_z_up_mat * self.flip_y_mat
            self.up_vector = Vector((0, 1, 0))
            self.forward_vector = Vector((0, 0, 1))
        else:
            self.error("Invalid coordinate system '{}' in .egg file.".format(coordsys))
            return

        if self.coord_system is not None and self.coord_system != coordsys:
            self.error("Mismatching <CoordinateSystem> tags in .egg file.")
            return

        self.inv_cs_matrix = self.cs_matrix.inverted()
        self.coord_system = coordsys

    def transform_matrix(self, matrix):
        """ Transforms the given matrix from the egg file's coordinate system
        into the Z-Up-Right coordinate system. """

        if self.coord_system == 'ZUP':
            return matrix
        else:
            return self.inv_cs_matrix * matrix * self.cs_matrix

    def final_report(self):
        """ Makes error messages about things that are tallied up, such as
        duplicate faces.  Called after importing is done. """

        if self.duplicate_faces > 0:
            self.warn("Removed {} duplicate faces".format(self.duplicate_faces))

        if self.degenerate_faces > 0:
            self.warn("Removed {} degenerate faces".format(self.degenerate_faces))

    def load_image(self, path):
        """ Loads an image from disk as Blender image. """

        if sys.platform == 'win32':
            # Convert an absolute Panda-style path to a Windows path.
            if len(path) > 3 and path[0] == '/' and path[2] == '/':
                path = path.replace('/', '\\')
                path = path[1].upper() + ':' + path[2:]

        path = path.replace('/', os.sep)

        # If it's a relative path, search in the location of the .egg first.
        if not os.path.isabs(path) and self.search_dir and os.path.exists(os.path.join(self.search_dir, path)):
            path = os.path.join(self.search_dir, path)
            path = path.replace(os.sep + '.' + os.sep, os.sep)
            image = bpy.data.images.load(path)
            #image.filepath = path
        else:
            # Try loading it with the original path, just in case.
            try:
                image = bpy.data.images.load(path)
            except RuntimeError:
                # That failed, of course.  OK, create a new image with this
                # filename, and issue an error.
                image = bpy.data.images.new(os.path.basename(path), 1, 1)
                image.source = 'FILE'
                image.filepath = path
                self.error("Unable to find texture {}".format(path))

        return image

    def assign_vertex_groups(self):
        """ Called at the end, to assign all of the vertex groups. """

        for name, vertex_ref in self.group_vertex_refs:
            vpool = self.vertex_pools[vertex_ref.pool]
            for group in vpool.groups:
                vertex_groups = group.mesh_object.vertex_groups
                if name in vertex_groups:
                    vertex_group = vertex_groups[name]
                else:
                    vertex_group = vertex_groups.new(name)

                # Remap the indices to this object.
                indices = set()
                for index in vertex_ref.indices:
                    vertex = vpool[index]
                    if vertex in group.vertices:
                        indices.add(group.vertices[vertex])

                if indices:
                    vertex_group.add(tuple(indices), vertex_ref.membership, 'ADD')

        self.group_vertex_refs.clear()

    def get_external_group(self, path):
        """ Returns the group used for an external reference. """

        if path in self.external_groups:
            return self.external_groups[path]

        group = bpy.data.groups.new(path)
        self.external_groups[path] = group
        return group

    def load_external_references(self):
        """ Resolves external file references. """

        if not self.external_groups:
            pass

        orig_scene = bpy.context.scene
        orig_search_dir = self.search_dir

        # Please note that things may be added to self.external_groups
        # recursively.

        for path, group in self.external_groups.items():
            # Create a separate scene for this model.
            scene = bpy.data.scenes.new(path)
            bpy.context.screen.scene = scene

            # Convert the external scene.
            path = os.path.join(orig_search_dir, path)
            self.search_dir = os.path.dirname(path)
            root = self.read_file(path)
            root.build_tree(self)
            self.assign_vertex_groups()

            # Assign all objects in the loaded scene to the group.
            for obj in scene.objects:
                group.objects.link(obj)

        bpy.context.screen.scene = orig_scene
        self.search_dir = orig_search_dir


class EggRenderMode:
    """ Accumulates render state attributes. """

    def __init__(self, parent):
        if parent is None:
            self.alpha_mode = None
            self.depth_write_mode = None
            self.depth_test_mode = None
            self.visibility_mode = None
            self.depth_offset = None
            self.draw_order = None
            self.bin = None
        else:
            self.alpha_mode = parent.alpha_mode
            self.depth_write_mode = parent.depth_write_mode
            self.depth_test_mode = parent.depth_test_mode
            self.visibility_mode = parent.visibility_mode
            self.depth_offset = parent.depth_offset
            self.draw_order = parent.draw_order
            self.bin = parent.bin

    def parse_scalar(self, name, value):
        pass


class EggMaterial:
    __slots__ = 'name', 'base', 'diff', 'amb', 'emit', 'spec', 'shininess', 'roughness', 'metallic', 'ior', 'materials'
    def __init__(self, name):
        self.name = name

        self.base = [1, 1, 1, 1]
        self.diff = [1, 1, 1, 1]
        self.amb = [1, 1, 1, 1]
        self.emit = [0, 0, 0, 1]
        self.spec = [0, 0, 0, 1]
        self.shininess = 0
        self.roughness = 1
        self.metallic = 0
        self.ior = 1

        self.materials = {}

    def begin_child(self, context, type, name, values):
        if type.upper() in ('SCALAR', 'CHAR*'):
            name = name.lower()
            value = parse_number(values[0])

            if name == 'baser':
                self.base[0] = value
            elif name == 'baseg':
                self.base[1] = value
            elif name == 'baseb':
                self.base[2] = value
            elif name == 'basea':
                self.base[3] = value
            elif name == 'diffr':
                self.diff[0] = value
            elif name == 'diffg':
                self.diff[1] = value
            elif name == 'diffb':
                self.diff[2] = value
            elif name == 'diffa':
                self.diff[3] = value
            elif name == 'ambr':
                self.amb[0] = value
            elif name == 'ambg':
                self.amb[1] = value
            elif name == 'ambb':
                self.amb[2] = value
            elif name == 'amba':
                self.amb[3] = value
            elif name == 'emitr':
                self.emit[0] = value
            elif name == 'emitg':
                self.emit[1] = value
            elif name == 'emitb':
                self.emit[2] = value
            elif name == 'emita':
                self.emit[3] = value
            elif name == 'specr':
                self.spec[0] = value
            elif name == 'specg':
                self.spec[1] = value
            elif name == 'specb':
                self.spec[2] = value
            elif name == 'speca':
                self.spec[3] = value
            elif name == 'shininess':
                self.shininess = value
            elif name == 'roughness':
                self.roughness = value
            elif name == 'metallic':
                self.metallic = value
            elif name == 'ior':
                self.ior = value

    def get_material(self, textures, color, bface, alpha):
        """ Returns the material for the indicated primitive. """

        if len(textures) == 0 and self is EggPrimitive.default_material and not bface and not alpha:
            return None

        key = (tuple(textures), color, bface, alpha)
        if key in self.materials:
            return self.materials[key]

        bmat = bpy.data.materials.new(self.name)
        bmat.diffuse_intensity = 1.0
        bmat.specular_intensity = 1.0
        bmat.specular_hardness = self.shininess * 2

        if not any(self.spec) and not any(self.diff) and not any(self.amb):
            # This is YABEE's way of making a shadeless material.
            bmat.use_shadeless = True
            bmat.diffuse_color = self.emit[:3]
        else:
            bmat.diffuse_color = self.diff[:3]
            bmat.specular_color = self.spec[:3]
            bmat.specular_alpha = self.spec[3]

            # Blender only supports one ambient value, so we average it.
            bmat.ambient = (self.amb[0] + self.amb[1] + self.amb[2]) / 3

            # Same for emission, except that it specifes the emission as a product
            # of the diffuse color, so we have to divide it.
            if any(bmat.diffuse_color):
                bmat.emit = sum(self.emit[:3]) / sum(bmat.diffuse_color)

        if alpha:
            alpha = alpha.lower()
            if alpha == 'off':
                bmat.game_settings.alpha_blend = 'OPAQUE'
            elif alpha.startswith('ms'):
                bmat.game_settings.alpha_blend = 'ALPHA_ANTIALIASING'
            elif alpha == 'binary':
                bmat.game_settings.alpha_blend = 'CLIP'
            else:
                bmat.game_settings.alpha_blend = 'ALPHA'

        bmat.game_settings.use_backface_culling = not bface

        for i, texture in enumerate(textures):
            slot = bmat.texture_slots.add()
            slot.texture = texture.texture
            slot.uv_layer = texture.uv_name or "UVMap"

            # Convert the Panda texture transform to the equivalent Blender
            # transform.  Ignores rotation, shear, or axis remap.
            m = texture.matrix
            if m is not None:
                pos = Vector((m[0][3], m[1][3], m[2][3]))
                slot.scale = (m[0][0], m[1][1], m[2][2])
                slot.offset = pos + (slot.scale - Vector((1, 1, 1))) * 0.5

            if texture.envtype == 'modulate':
                slot.use_map_color_diffuse = True
            elif texture.envtype == 'normal':
                slot.use_map_color_diffuse = False
                slot.use_map_normal = True
            elif texture.envtype == 'glow':
                slot.use_map_color_diffuse = True
                slot.use_map_emit = True
            elif texture.envtype == 'gloss':
                slot.use_map_color_diffuse = True
                slot.use_map_specular = True

            # Should probably be more sophisticated; right now this is to
            # support what YABEE generates.
            if texture.blend == 'add' and not alpha:
                bmat.game_settings.alpha_blend = 'ADD'

        self.materials[key] = bmat
        return bmat


class EggTexture:
    def __init__(self, name, image):
        self.texture = bpy.data.textures.new(name, 'IMAGE')
        self.texture.image = image
        self.envtype = 'modulate'
        self.uv_name = None
        self.matrix = None
        self.priority = 0
        self.blend = None
        self.warned_vpools = set()

    def begin_child(self, context, type, name, values):
        type = type.upper()

        if type in ('SCALAR', 'CHAR*'):
            name = name.lower()

            if name == 'wrap':
                value = values[0].lower()
                if value == 'repeat':
                    self.texture.extension = 'REPEAT'
                elif value == 'clamp':
                    self.texture.extension = 'EXTEND'
                elif value in ('border_color', 'border-color'):
                    self.texture.extension = 'CLIP'

            elif name == 'envtype':
                self.envtype = values[0].lower()
                if self.envtype == 'normal':
                    self.texture.use_normal_map = True

            elif name == 'minfilter':
                if 'mipmap' in values[0].lower():
                    self.texture.use_mipmap = True

            elif name == 'alpha':
                if values[0].lower() == 'premultiplied':
                    self.texture.image.alpha_mode = 'PREMUL'

            elif name == 'blend':
                self.blend = values[0].lower()

            elif name == 'uv_name' or name == 'uv-name':
                self.uv_name = values[0]

            elif name == 'priority':
                self.priority = int(values[0])

        elif type == 'TRANSFORM':
            return EggTransform()

    def end_child(self, context, type, name, child):
        if isinstance(child, EggTransform):
            if self.matrix is not None:
                self.matrix *= child.matrix
            else:
                self.matrix = child.matrix


class EggTransform:
    __slots__ = 'matrix',

    def __init__(self):
        self.matrix = Matrix()

    def begin_child(self, context, type, name, values):
        v = [parse_number(v) for v in values]

        type = type.upper()
        if type == 'TRANSLATE':
            if len(values) == 2:
                self.matrix = Matrix.Translation(v + [0]) * self.matrix
            else:
                self.matrix = Matrix.Translation(v) * self.matrix

        elif type == 'ROTATE':
            self.matrix = Matrix.Rotation(radians(v[0]), 4, v[1:] or (0, 0, 1)) * self.matrix

        elif type == 'ROTX':
            self.matrix = Matrix.Rotation(radians(v[0]), 4, 'X') * self.matrix

        elif type == 'ROTY':
            self.matrix = Matrix.Rotation(radians(v[0]), 4, 'Y') * self.matrix

        elif type == 'ROTZ':
            self.matrix = Matrix.Rotation(radians(v[0]), 4, 'Z') * self.matrix

        elif type == 'SCALE':
            if len(v) == 1:
                x = y = z = v[0]
            elif len(v) == 2:
                x, y = v
                z = 1
            else:
                x, y, z = v
            self.matrix = Matrix(((x, 0, 0, 0), (0, y, 0, 0), (0, 0, z, 0), (0, 0, 0, 1))) * self.matrix

        elif type == 'MATRIX3':
            self.matrix = Matrix(((v[0], v[3],  0.0, v[6]),
                                  (v[1], v[4],  0.0, v[7]),
                                  ( 0.0,  0.0,  1.0,  0.0),
                                  (v[2], v[5],  0.0, v[8]))) * self.matrix

        elif type == 'MATRIX4':
            self.matrix = Matrix(((v[0], v[4], v[8], v[12]),
                                  (v[1], v[5], v[9], v[13]),
                                  (v[2], v[6], v[10], v[14]),
                                  (v[3], v[7], v[11], v[15]))) * self.matrix


class EggVertex:
    __slots__ = 'pos', 'normal', 'color', 'uv_map', 'aux_map', 'dxyzs'

    def __init__(self, pos):
        self.pos = pos
        self.normal = None
        self.color = None
        self.uv_map = {}
        self.aux_map = {}
        self.dxyzs = {}

    def begin_child(self, context, type, name, values):
        type = type.upper()

        if type == 'NORMAL':
            self.normal = tuple(parse_number(v) for v in values)

        elif type == 'RGBA':
            self.color = tuple(parse_number(v) for v in values)

        elif type == 'UV':
            self.uv_map[name or DEFAULT_UV_NAME] = [parse_number(v) for v in values]

        elif type == 'AUX':
            self.aux_map[name] = [parse_number(v) for v in values]

        elif type == 'DXYZ':
            if not name:
                name = values.pop(0)
            self.dxyzs[name] = tuple(parse_number(v) for v in values)

    def __hash__(self):
        return hash(self.pos)

    def __eq__(self, other):
        return self.pos == other.pos

    def __ne__(self, other):
        return self.pos != other.pos


class EggVertexPool:
    def __init__(self, name):
        self.name = name
        self._vertices = []
        self.groups = set()

    def __getitem__(self, index):
        if index < 0:
            raise IndexError
        vertex = self._vertices[index]
        if not vertex:
            raise IndexError
        return vertex

    def begin_child(self, context, type, name, values):
        if type.upper() != 'VERTEX':
            assert False

        return EggVertex(tuple(parse_number(v) for v in values))

    def end_child(self, context, type, name, vertex):
        verts = self._vertices
        if name:
            # Add the vertex at the requested index.
            num_vertices = len(verts)
            index = int(name)
            if index < num_vertices:
                assert verts[index] is None
                verts[index] = vertex
            else:
                if index != num_vertices:
                    verts.extend([None] * (index - num_vertices))
                verts.append(vertex)
        else:
            verts.append(vertex)


class EggPrimitive:
    __slots__ = 'indices', 'pool', 'material', 'textures', 'normal', 'color', 'bface', 'alpha', 'visibility'

    default_material = EggMaterial("default")

    def __init__(self):
        self.material = EggPrimitive.default_material
        self.color = (1, 1, 1, 1)
        self.normal = None
        self.bface = False
        self.alpha = None
        self.visibility = None
        self.textures = []

    def begin_child(self, context, type, name, values):
        type = type.upper()

        if type == 'VERTEXREF':
            self.indices = tuple(int(v) for v in values)
            return self # To catch the <Ref>

        elif type == 'REF':
            self.pool = values[0]

        elif type == 'SCALAR' or type == 'CHAR*':
            name = name.lower()

        elif type == 'TREF':
            self.textures.append(context.textures[values[0]])

        elif type == 'MREF':
            self.material = context.materials[values[0]]

        elif type == 'NORMAL':
            self.normal = tuple(parse_number(v) for v in values)

        elif type == 'RGBA':
            self.color = tuple(parse_number(v) for v in values)


class EggTriangleStrip(EggPrimitive):

    __slots__ = 'components'

    def begin_child(self, context, type, name, values):
        if type.upper() == 'VERTEXREF':
            indices = [int(v) for v in values]
            self.indices = tuple(indices)
            self.components = []
            prevprev = indices.pop(0)
            prev = indices.pop(0)
            flip = False
            while indices:
                index = indices.pop(0)
                prim = EggPrimitive()
                # I don't think the flipping is truly necessary for Blender.
                if flip:
                    prim.indices = [prev, prevprev, index]
                    flip = False
                else:
                    prim.indices = [prevprev, prev, index]
                    flip = True
                # It's fine to copy over the attributes, since the .egg syntax
                # only allows per-component settings after the <VertexRef>.
                prim.material = self.material
                prim.color = self.color
                prim.normal = self.normal
                prim.bface = self.bface
                prim.alpha = self.alpha
                prim.visibility = self.visibility
                prim.textures = self.textures
                prevprev = prev
                prev = index
                self.components.append(prim)
            return self # To catch the <Ref>

        elif type.upper() == 'COMPONENT':
            index = int(name)
            return self.components[index]
        else:
            EggPrimitive.begin_child(self, context, type, name, values)


class EggTriangleFan(EggPrimitive):

    __slots__ = 'components'

    def begin_child(self, context, type, name, values):
        if type.upper() == 'VERTEXREF':
            indices = [int(v) for v in values]
            self.indices = tuple(indices)
            self.components = []
            first = indices.pop(0)
            prev = indices.pop(0)
            while indices:
                index = indices.pop(0)
                prim = EggPrimitive()
                prim.indices = [first, prev, index]
                # It's fine to copy over the attributes, since the .egg syntax
                # only allows per-component settings after the <VertexRef>.
                prim.material = self.material
                prim.color = self.color
                prim.normal = self.normal
                prim.bface = self.bface
                prim.alpha = self.alpha
                prim.visibility = self.visibility
                prim.textures = self.textures
                prev = index
                self.components.append(prim)
            return self # To catch the <Ref>

        elif type.upper() == 'COMPONENT':
            index = int(name)
            return self.components[index]
        else:
            EggPrimitive.begin_child(self, context, type, name, values)


class EggNode:
    pass


class EggGroupNode(EggNode):
    def __init__(self):
        self.children = []
        self.external_refs = []

    def begin_child(self, context, type, name, values):
        type = type.upper()

        if type == 'COORDINATESYSTEM':
            assert len(values) == 1
            context.set_coordinate_system(values[0])
        elif type == 'TEXTURE':
            tex = EggTexture(name, context.load_image(values[0]))
            context.textures[name] = tex
            return tex
        elif type == 'MATERIAL':
            mat = EggMaterial(name)
            context.materials[name] = mat
            return mat
        elif type == 'VERTEXPOOL':
            vpool = EggVertexPool(name)
            context.vertex_pools[name] = vpool
            return vpool
        elif type == 'FILE':
            self.external_refs.append((name, values[0]))
        elif type in ('GROUP', 'INSTANCE'):
            group = EggGroup(name, parent=self)
            group.instance_type = (type == 'INSTANCE')
            return group
        elif type == 'JOINT':
            joint = EggJoint(name, parent=self)
            context.joints[name] = joint
            return joint
        elif type == 'POLYGON':
            return EggPrimitive()
        elif type == 'TRIANGLEFAN':
            return EggTriangleFan()
        elif type == 'TRIANGLESTRIP':
            return EggTriangleStrip()
        elif type == 'PATCH':
            pass
        elif type == 'POINTLIGHT':
            pass
        elif type == 'LINE':
            pass
        elif type == 'NURBSSURFACE':
            pass
        elif type == 'NURBSCURVE':
            pass
        elif type == 'TABLE':
            return EggTable(name)
        elif type == 'ANIMPRELOAD':
            pass

    def end_child(self, context, type, name, child):
        if isinstance(child, EggNode):
            self.children.append(child)

    def build_tree(self, context, parent=None, inv_matrix=None, under_dart=False):
        for child in self.children:
            child.build_tree(context, parent, inv_matrix, under_dart)

    def build_armature(self, *args, **kwargs):
        """ Recursively builds up an armature under a group with dart tag.
        This requires the armature to be active and in edit mode. """

        for child in self.children:
            child.build_armature(*args, **kwargs)

    def apply_default_pose(self, context, pose):
        """ Recursively applies the default pose to the model. """

        for child in self.children:
            child.apply_default_pose(context, pose)


class EggGroup(EggGroupNode):
    def __init__(self, name, parent):
        EggGroupNode.__init__(self)
        self.name = name
        self.instance_type = False
        self.properties = {}

        self.vertices = {}

        self.matrix = None
        self.default_pose = None
        self.mesh = None
        self.first_vertex = 0
        self.normals = []
        self.have_normals = False
        self.vertex_colors = []
        self.have_vertex_colors = False
        self.shape_keys = set()
        self.materials = []
        self.dart = False
        self.external_instance = None
        self.has_billboard = False
        self.has_billboard_center = False

        # Keep track of whether there is any geometry below this node.
        self.any_geometry_below = False
        self.has_default_pose = False

    def is_instance_type(self):
        """ Returns true if this begins a new coordinate space. """

        return self.instance_type or (self.has_billboard and not self.has_billboard_center)

    def get_bvert(self, vert):
        # Vertices are keyed by position only, since normals and UVs are
        # defined per-loop.
        vertices = self.vertices
        if vert in vertices:
            return vertices[vert]

        mesh = self.mesh
        index = len(mesh.vertices)
        mesh.vertices.add(1)
        bvert = mesh.vertices[index]
        bvert.co = vert.pos
        vertices[vert] = index

        self.shape_keys.update(vert.dxyzs.keys())
        return index

    def begin_child(self, context, type, name, values):
        orig_type = type
        type = type.upper()

        #if type in ('SCALAR', 'CHAR*', 'BILLBOARD', 'DCS', 'DART', 'SWITCH', 'OBJECTTYPE', 'TAG', 'MODEL', 'TEXLIST', 'REF'):

        if type in ('SCALAR', 'CHAR*'):
            name = name.lower().replace('_', '-')

            # YABEE recognizes these scalars as game properties.
            if name in ('collide-mask', 'from-collide-mask', 'into-collide-mask', 'bin', 'draw-order'):
                self.properties[name] = values[0]

        elif type in ('COLLIDE', 'OBJECTTYPE'):
            self.properties[orig_type] = values[0]

        elif type == 'TAG':
            # Odd, but the reference .egg parser really intentionally joins
            # multiple values using newlines when parsing the <Tag> body.
            self.properties[name] = '\n'.join(values)

        elif type == 'TRANSFORM':
            return EggTransform()

        elif type == 'VERTEXREF':
            vertex_ref = EggGroupVertexRef([int(v) for v in values])
            context.group_vertex_refs.append((self.name, vertex_ref))
            return vertex_ref

        elif type == 'DART':
            # This indicates the root of an animated model.
            # Do we need to consider other dart types?
            self.dart = values[0].strip().lower() not in ('0', 'none')

        elif type == 'DEFAULTPOSE':
            return EggTransform()

        elif type == 'BILLBOARD':
            self.has_billboard = (values[0].lower() != 'none')

        elif type == 'BILLBOARDCENTER':
            self.has_billboard_center = True

        return EggGroupNode.begin_child(self, context, type, name, values)

    def end_child(self, context, type, name, child):
        if isinstance(child, EggTransform):
            if type.upper() == 'DEFAULTPOSE':
                self.has_default_pose = True
                if self.default_pose is not None:
                    self.default_pose *= child.matrix
                else:
                    self.default_pose = child.matrix
            else:
                if self.matrix is not None:
                    self.matrix *= child.matrix
                else:
                    self.matrix = child.matrix

        elif isinstance(child, EggPrimitive):
            self.any_geometry_below = True

            vpool = context.vertex_pools[child.pool]
            vpool.groups.add(self)

            if self.mesh is None:
                self.mesh = bpy.data.meshes.new(self.name)

            if hasattr(child, 'components'):
                for component in child.components:
                    self.add_polygon(context, component, vpool)
            else:
                self.add_polygon(context, child, vpool)

        elif isinstance(child, EggGroup):
            if type.upper() == 'INSTANCE' and (not self.matrix or not child.matrix) and \
                not child.children and len(child.external_refs) == 1:
                # YABEE exports a single instance containing a <File> from a
                # game property named 'file'.  flt2egg puts a <Transform>
                # inside the <Instance>.  We will support both.
                ref = child.external_refs[0][1]
                self.external_instance = (ref, child)
                return

            self.any_geometry_below |= child.any_geometry_below
            self.has_default_pose |= child.has_default_pose

        return EggGroupNode.end_child(self, context, type, name, child)

    def add_polygon(self, context, prim, vpool):
        if prim.normal:
            self.have_normals = True
        poly_normal = prim.normal or (0, 0, 0)

        # Create a polygon.
        mesh = self.mesh
        poly_index = len(mesh.polygons)
        mesh.polygons.add(1)
        poly = mesh.polygons[poly_index]

        # Create the loops.  A loop is an occurrence of a vertex in a polygon.
        loops = mesh.loops
        loop_offset = len(loops)
        loops.add(len(prim.indices))
        for index, loop in zip(prim.indices, loops[loop_offset:]):
            try:
                vertex = vpool[index]
            except IndexError:
                context.error("Primitive references index {}, which is not defined in vertex pool '{}'".format(index, vpool.name))
                # Skip the face.  This will leave some unused loops, but
                # they will be cleaned up by validate().
                return

            loop.vertex_index = self.get_bvert(vertex)

            vertex_normal = vertex.normal
            if vertex_normal:
                self.have_normals = True
                self.normals.append(vertex_normal or poly_normal)
                poly.use_smooth = True
            else:
                self.normals.append(vertex_normal or poly_normal)

            if vertex.color:
                self.have_vertex_colors = True
                self.vertex_colors += vertex.color[:3]
            else:
                self.vertex_colors += (1, 1, 1)

            for name, uv in vertex.uv_map.items():
                if name not in mesh.uv_layers:
                    mesh.uv_textures.new(name)
                mesh.uv_layers[name].data[loop.index].uv = uv

        # Reference those loops in the polygon.
        poly.loop_start = loop_offset
        poly.loop_total = len(prim.indices)

        # Assign the highest priority texture that uses a given UV set to
        # the UV texture.  If there are multiple textures with the same
        # priority, use the first one.
        set_textures = {}
        for texture in prim.textures:
            uv_name = texture.uv_name or DEFAULT_UV_NAME
            try:
                uv_texture = mesh.uv_textures[uv_name]
            except KeyError:
                # Display a warning.  Since this will probably be the case
                # for every polygon in this mesh, display it only once.
                if vpool.name not in texture.warned_vpools:
                    texture.warned_vpools.add(vpool.name)
                    context.warn("Texture {} references UV set {} which is not present on any vertex in {}".format(texture.texture.name, texture.uv_name, self.name))
                continue

            if uv_name not in set_textures or texture.priority > set_textures[uv_name].priority:
                set_textures[uv_name] = texture
                uv_texture.data[poly_index].image = texture.texture.image

        # Check if we already have a material for this combination.
        bmat = prim.material.get_material(prim.textures, prim.color, prim.bface, prim.alpha)
        if bmat in self.materials:
            index = self.materials.index(bmat)
        else:
            index = len(self.materials)
            self.materials.append(bmat)
            mesh.materials.append(bmat)
        poly.material_index = index

    def build_tree(self, context, parent, inv_matrix=None, under_dart=False):
        """ Walks the hierarchy of groups and builds the Blender object graph.
        This needs to happen after adding all the children so that we fully
        know the parent-child hierarchy and transforms. """

        data = None
        self.mesh_object = None
        if self.mesh:
            data = self.mesh
            data.update(calc_edges=True, calc_tessface=True)
            if self.have_normals:
                # Check if the mesh just uses smooth normals.  If so, don't
                # bother importing custom normals.
                data.calc_normals()
                max_diff = 0
                for normal1, l in zip(self.normals, data.loops):
                    normal2 = data.vertices[l.vertex_index].normal
                    diff = (normal2 - Vector(normal1)).length_squared
                    max_diff = max(diff, max_diff)

                if max_diff > 0.01:
                    data.normals_split_custom_set(self.normals)
                    data.use_auto_smooth = True

            if self.have_vertex_colors:
                cols = data.vertex_colors.new()
                cols.data.foreach_set('color', self.vertex_colors)

            if data.validate(verbose=True):
                context.info("Corrected invalid geometry in mesh '{}'.".format(data.name))

        if self.dart and not under_dart:
            if data:
                # We already have object data.  Move the geometry to a child
                # object.
                self.mesh_object = bpy.data.objects.new("", data)
            data = bpy.data.armatures.new(self.name)

        object = bpy.data.objects.new(self.name, data)
        object.parent = parent
        self.object = object

        if object.type == 'MESH':
            self.mesh_object = object

        # Let the user know if we couldn't get the name we want.
        if object.name != self.name:
            context.warn("'{}' was renamed to '{}' due to a name conflict".format(self.name, object.name))

        if data and data.name != self.name:
            if data.name != object.name:
                context.warn("'{}' was renamed to '{}' due to a name conflict".format(self.name, data.name))

        # Check if this group contains an external instance, such as created
        # by YABEE or flt2egg.
        if self.external_instance:
            file, instance = self.external_instance
            self.properties['file'] = file
            if instance.matrix and not self.matrix and not self.children and data is None:
                # We can safely copy the matrix from the child.
                self.matrix = instance.matrix
            object.dupli_type = 'GROUP'
            object.dupli_group = context.get_external_group(file)

        if not inv_matrix:
            inv_matrix = context.inv_cs_matrix

        if self.matrix:
            # Adjust the matrix to be consistent with the coordinate system.
            matrix = context.transform_matrix(self.matrix)
            object.matrix_basis = matrix

            inv_matrix = matrix.inverted() * inv_matrix

        if self.is_instance_type():
            inv_matrix = context.inv_cs_matrix

        # The .egg format specifies vertex data in global space, so we have to
        # transform the object by its inverse matrix to compensate for that.
        if inv_matrix and object.type == 'MESH':
            object.data.transform(inv_matrix)

        # Place it in the scene.  We need to do this before assigning game
        # properties, below.
        bpy.context.scene.objects.link(object)

        if self.mesh_object and object is not self.mesh_object:
            self.mesh_object.parent = object
            bpy.context.scene.objects.link(self.mesh_object)

        # Recurse.
        for child in self.children:
            child.build_tree(context, object, inv_matrix, under_dart or self.dart)

        # Awkward, but it seems there's no other way to set a game property
        # or create bones or add shape keys.
        if self.properties or self.dart or self.shape_keys:
            active = bpy.context.scene.objects.active
            bpy.context.scene.objects.active = object
            for name, value in self.properties.items():
                bpy.ops.object.game_property_new(type='STRING', name=name)
                object.game.properties[name].value = value

            if self.shape_keys:
                # Add the basis key first.
                bpy.ops.object.shape_key_add()
                basis_data = bpy.context.object.active_shape_key.data

                for key in sorted(self.shape_keys):
                    bpy.ops.object.shape_key_add()
                    shape_key = bpy.context.object.active_shape_key
                    shape_key.name = key
                    shape_key.slider_min = -10
                    shape_key.slider_max = 10
                    data = shape_key.data

                    for vert, index in self.vertices.items():
                        dxyz = vert.dxyzs.get(key)
                        if dxyz:
                            data[index].co = basis_data[index].co + Vector(dxyz)

            if self.dart and not under_dart:
                #bpy.context.scene.update()
                bpy.ops.object.mode_set(mode='EDIT')
                self.build_armature(context, object, None, Matrix())
                bpy.ops.object.mode_set(mode='OBJECT')

                # If any of the joints below this level define a DefaultPose,
                # apply this to the pose bones.
                if self.has_default_pose:
                    self.apply_default_pose(context, object.pose)

            bpy.context.scene.objects.active = active

        return object

    def build_armature(self, context, armature, parent, matrix):
        """ Recursively builds up an armature under a group with dart tag.
        This requires the armature to be active and in edit mode. """

        if self.mesh_object:
            # Add an armature modifier.
            mod = self.mesh_object.modifiers.new(armature.data.name, 'ARMATURE')
            mod.object = armature

        EggGroupNode.build_armature(self, context, armature, parent, matrix)


class EggJoint(EggGroup):
    def build_tree(self, context, parent, inv_matrix=None, under_dart=False):
        # We don't export joints unless they have geometry below them.
        if self.any_geometry_below:
            EggGroup.build_tree(self, context, parent, inv_matrix, under_dart)

    def build_armature(self, context, armature, parent, matrix):
        """ Recursively builds up an armature under a group with dart tag.
        This requires the armature to be active and in edit mode. """

        if self.matrix:
            matrix *= context.transform_matrix(self.matrix)

        # Blender has a concept of "bone length", but Panda does not.  This
        # means we have to guess the bone length if we want sightly armatures.

        bone = armature.data.edit_bones.new(self.name)
        bone.parent = parent
        bone.tail = Vector((0, 1, 0))
        bone.matrix = matrix
        self.bone_name = bone.name

        # Find the closest child that lies directly along the length of this
        # bone.  That child's head becomes this bone's tail.
        # We only consider direct children; we assume that if there's an
        # intervening <Group>, the bones were meant to be disconnected.
        bone_dir = bone.tail - bone.head
        bone_dir.normalize()
        connect_child = None
        connect_child_dist = None
        average_dist = 0.0
        num_direct_children = 0

        for child in self.children:
            # Recurse.  It will return a bone if the child is an EggJoint.
            child_bone = child.build_armature(context, armature, bone, matrix)
            if child_bone:
                vec = child_bone.head - bone.head
                dist = bone_dir.dot(vec)
                average_dist += dist
                num_direct_children += 1

                if dist > 0.0001 and bone_dir.dot(vec.normalized()) >= 0.99999:
                    # Yes, it lies along the length.
                    if connect_child_dist is None or dist < connect_child_dist:
                        connect_child = child_bone
                        connect_child_dist = dist

        if connect_child:
            # Yes, there is a child directly along the bone's axis.
            bone.tail = connect_child.head
            connect_child.use_connect = True
        elif num_direct_children > 0:
            # No, use the average of the bone's children.
            length = average_dist / num_direct_children
            if length > 0.0001:
                bone.length = length
        else:
            # An extremity.  Um, why not check whether *any* bone starts on
            # this bone's axis, and use that as length, because that happens
            # to work perfectly for my test model.
            # Ideally this would check all bones, not just bones already
            # visited, but that would require overhauling the traversal order.
            connect = None
            connect_dist = None
            for other_bone in armature.data.edit_bones:
                vec = other_bone.head - bone.head
                if bone != other_bone and bone_dir.dot(vec.normalized()) >= 0.99999:
                    # Yes, it lies along the length.
                    dist = bone_dir.dot(vec)
                    if dist > 0.001 and (connect_dist is None or dist < connect_dist):
                        connect = other_bone
                        connect_dist = dist
            if connect:
                bone.tail = connect.head
            elif parent:
                # Otherwise, inherit the length from the distance to the
                # parent bone.  This is a guess, but not such a bad one.
                parent_length = (bone.head - parent.head).length
                if parent_length > 0.0001:
                    bone.length = parent_length
                else:
                    bone.length = parent.length

        # Connect all the bone's children that match up well.
        for child in bone.children:
            if (bone.tail - child.head).length_squared < 0.0001:
                child.use_connect = True

        return bone

    def apply_default_pose(self, context, pose):
        """ Recursively applies the default pose to the model. """

        matrix = self.default_pose or self.matrix or Matrix.Identity(4)
        matrix = context.transform_matrix(matrix)

        pose_bone = pose.bones[self.bone_name]
        if pose_bone.parent:
            matrix = pose_bone.parent.matrix * matrix
        pose_bone.matrix = matrix

        EggGroupNode.apply_default_pose(self, context, pose)


class EggGroupVertexRef:

    __slots__ = 'indices', 'membership', 'pool'

    def __init__(self, indices):
        self.indices = indices
        self.membership = 1.0

    def begin_child(self, context, type, name, values):
        if type.upper() in ('SCALAR', 'CHAR*'):
            name = name.lower()
            value = parse_number(values[0])

            if name == 'membership':
                self.membership = value

        elif type.upper() == 'REF':
            self.pool = values[0]


class EggTable(EggGroupNode):
    def __init__(self, name):
        EggGroupNode.__init__(self)
        self.name = name

    def begin_child(self, context, type, name, values):
        type = type.upper()

        if type == 'TABLE':
            return EggTable(name)
        elif type == 'BUNDLE':
            return EggBundle(name)
        elif type == 'XFM$ANIM':
            return EggXfmSAnim()
        elif type == 'XFM$ANIM_S$':
            return EggXfmSAnim_S()
        elif type == 'S$ANIM':
            return EggSAnim(name)

    def build_animations(self, context, bundle):
        for child in self.children:
            if isinstance(child, EggXfmSAnim):
                bundle.add_curves(context, self.name, child)
            else:
                child.build_animations(context, bundle)


class EggBundle(EggTable):
    def __init__(self, name):
        EggTable.__init__(self, name)
        self.skeleton = None
        self.morph = None

    def end_child(self, context, type, name, child):
        if child.name == '<skeleton>':
            self.skeleton = child
        elif child.name == 'morph':
            self.morph = child

    def build_tree(self, context, parent=None, inv_matrix=None, under_dart=False):
        if self.skeleton:
            self.action = bpy.data.actions.new(self.name)
            self.action.use_fake_user = True

            self.skeleton.build_animations(context, self)

        if self.morph:
            morph_action = bpy.data.actions.new(self.name)
            morph_action.use_fake_user = True
            morph_action.id_root = 'KEY'

            for child in self.morph.children:
                if isinstance(child, EggSAnim):
                    self.add_morph(morph_action, child)

    def build_animations(self, context, bundle):
        context.error("Cannot have <Bundle> under another <Bundle>")
        return

    def add_curves(self, context, name, data):
        """ Adds the curves for the given joint from the given <Xfm$Anim>. """

        fcurves = self.action.fcurves
        prefix = 'pose.bones["{}"].'.format(name)

        # First, convert all per-frame data to matrices.  This is just easier.
        init_matrix = Matrix.Identity(4)
        num_frames = data.num_frames
        matrices = [init_matrix for i in range(num_frames)]

        joint_matrix = context.joints[name].matrix

        # Make sure all channels have all frames defined.
        channels = data.channels
        for c in channels:
            while len(channels[c]) < data.num_frames:
                channels[c].append(channels[c][-1])

        if 'i' in channels or 'j' in channels or 'k' in channels:
            if 'i' not in channels:
                channels['i'] = [1.0] * data.num_frames
            if 'j' not in channels:
                channels['j'] = [1.0] * data.num_frames
            if 'k' not in channels:
                channels['k'] = [1.0] * data.num_frames

        if 'x' in channels or 'y' in channels or 'z' in channels:
            if 'x' not in channels:
                channels['x'] = [0.0] * data.num_frames
            if 'y' not in channels:
                channels['y'] = [0.0] * data.num_frames
            if 'z' not in channels:
                channels['z'] = [0.0] * data.num_frames

        for o in data.order:
            if o == 's' and 'i' in channels and 'j' in channels and 'k' in channels:
                #TODO: shear?
                chan_x = channels['i']
                chan_y = channels['j']
                chan_z = channels['k']
                for i in range(num_frames):
                    matrices[i] = Matrix(((chan_x[i], 0, 0, 0),
                                          (0, chan_y[i], 0, 0),
                                          (0, 0, chan_z[i], 0),
                                          (0, 0, 0, 1))) * matrices[i]

            elif o == 'h' and 'h' in channels:
                for i, h in enumerate(channels['h']):
                    matrices[i] = Matrix.Rotation(radians(h), 4, context.up_vector) * matrices[i]

            elif o == 'p' and 'p' in channels:
                for i, p in enumerate(channels['p']):
                    matrices[i] = Matrix.Rotation(radians(p), 4, context.right_vector) * matrices[i]

            elif o == 'r' and 'r' in channels:
                if data.order == 'sphrt':
                    for i, r in enumerate(channels['r']):
                        matrices[i] = Matrix.Rotation(radians(-r), 4, context.forward_vector) * matrices[i]
                else:
                    for i, r in enumerate(channels['r']):
                        matrices[i] = Matrix.Rotation(radians(r), 4, context.forward_vector) * matrices[i]

            elif o == 't' and 'x' in channels and 'y' in channels and 'z' in channels:
                chan_x = channels['x']
                chan_y = channels['y']
                chan_z = channels['z']
                for i, v in enumerate(zip(chan_x, chan_y, chan_z)):
                    matrices[i] = Matrix.Translation(v) * matrices[i]

        # Multiply out the joint transform.
        for i, m in enumerate(matrices):
            matrices[i] = context.transform_matrix(joint_matrix.inverted() * m)

        if 'x' in channels or 'y' in channels or 'z' in channels:
            x_curve = fcurves.new(prefix + 'location', 0)
            y_curve = fcurves.new(prefix + 'location', 1)
            z_curve = fcurves.new(prefix + 'location', 2)
            x_curve.keyframe_points.add(num_frames)
            y_curve.keyframe_points.add(num_frames)
            z_curve.keyframe_points.add(num_frames)

            for i, m in enumerate(matrices):
                translation = m.to_translation()
                x_curve.keyframe_points[i].co = (i, translation[0])
                y_curve.keyframe_points[i].co = (i, translation[1])
                z_curve.keyframe_points[i].co = (i, translation[2])

            x_curve.update()
            y_curve.update()
            z_curve.update()

        if 'h' in channels or 'p' in channels or 'r' in channels:
            w_curve = fcurves.new(prefix + 'rotation_quaternion', 0)
            x_curve = fcurves.new(prefix + 'rotation_quaternion', 1)
            y_curve = fcurves.new(prefix + 'rotation_quaternion', 2)
            z_curve = fcurves.new(prefix + 'rotation_quaternion', 3)
            w_curve.keyframe_points.add(num_frames)
            x_curve.keyframe_points.add(num_frames)
            y_curve.keyframe_points.add(num_frames)
            z_curve.keyframe_points.add(num_frames)

            for i, m in enumerate(matrices):
                quaternion = m.to_quaternion()
                w_curve.keyframe_points[i].co = (i, quaternion.w)
                x_curve.keyframe_points[i].co = (i, quaternion.x)
                y_curve.keyframe_points[i].co = (i, quaternion.y)
                z_curve.keyframe_points[i].co = (i, quaternion.z)

            w_curve.update()
            x_curve.update()
            y_curve.update()
            z_curve.update()

        if 'i' in channels or 'j' in channels or 'k' in channels:
            x_curve = fcurves.new(prefix + 'scale', 0)
            y_curve = fcurves.new(prefix + 'scale', 1)
            z_curve = fcurves.new(prefix + 'scale', 2)
            x_curve.keyframe_points.add(num_frames)
            y_curve.keyframe_points.add(num_frames)
            z_curve.keyframe_points.add(num_frames)

            for i, m in enumerate(matrices):
                scale = m.to_scale()
                x_curve.keyframe_points[i].co = (i, scale[0])
                y_curve.keyframe_points[i].co = (i, scale[1])
                z_curve.keyframe_points[i].co = (i, scale[2])

            x_curve.update()
            y_curve.update()
            z_curve.update()

    def add_morph(self, action, data):
        """ Adds the curve for a morph target to this bundle's action. """

        fcurves = action.fcurves
        curve = fcurves.new('key_blocks["{}"].value'.format(data.name), 0)
        keyframe_points = curve.keyframe_points
        keyframe_points.add(len(data.values))

        for i, v in enumerate(data.values):
            keyframe_points[i].co = (i, v)


class EggXfmSAnim(EggGroupNode):
    def __init__(self):
        self.fps = None
        self.order = 'srpht'
        self.channels = {}
        self.num_frames = 0

    def begin_child(self, context, type, name, values):
        if type.upper() in ('SCALAR', 'CHAR*'):
            name = name.lower()

            if name == 'order':
                self.order = values[0].lower()
            elif name == 'fps':
                self.fps = parse_number(values[0])
            elif name == 'contents':
                self.contents = values[0].lower()

        elif type == 'V' or type == 'v':
            values = [parse_number(v) for v in values]
            num_channels = len(self.contents)
            self.num_frames = len(values) // len(self.contents)
            for i, c in enumerate(self.contents):
                self.channels[c] = values[i::num_channels]


class EggXfmSAnim_S(EggXfmSAnim):
    def begin_child(self, context, type, name, values):
        type = type.upper()

        if type in ('SCALAR', 'CHAR*'):
            name = name.lower()

            if name == 'order':
                self.order = values[0].lower()
            elif name == 'fps':
                self.fps = parse_number(values[0])
            elif name == 'contents':
                self.contents = values[0].lower()

        elif type == 'S$ANIM':
            return EggSAnim(name)

    def end_child(self, context, type, name, child):
        if isinstance(child, EggSAnim):
            self.channels[name] = child.values
            self.num_frames = max(self.num_frames, len(child.values))


class EggSAnim(EggNode):

    __slots__ = 'name', 'values'

    def __init__(self, name):
        self.name = name
        self.values = []

    def begin_child(self, context, type, name, values):
        if type.upper() == 'V':
            self.values += [parse_number(v) for v in values]
