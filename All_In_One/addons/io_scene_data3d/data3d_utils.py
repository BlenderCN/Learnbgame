import os.path
import logging

import struct
import json
import gzip
import re

import string
import random
import copy

__all__ = ['deserialize_data3d', 'serialize_data3d']

HEADER_BYTE_LENGTH = 16
MAGIC_NUMBER = '\x44\x33\x44\x41' #Fixme reverse byteorder: '\x41\x44\x33\x44' #AD3D encoded as ASCII characters in hex
VERSION = 1
SUFFIX_JSON = 'data3d.json'
SUFFIX_BUFFER = 'data3d.buffer'
SUFFIX_GZIP = 'gz'

ESCAPE_ASCII = re.compile(r'([\\"]|[^\ -~])')
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}

log = logging.getLogger('archilogic')

# Temp
dump_file = __file__.rsplit('.', 1)[0] + '.dump'


# Relevant Data3d keys
class D3D:
    # Root
    r_container = 'data3d'

    # Hierarchy
    node_id = 'nodeId'
    o_position = 'position'
    o_rotation = 'rotRad'
    o_meshes = 'meshes'
    o_mesh_keys = 'meshKeys'
    o_materials = 'materials'
    o_material_keys = 'materialKeys'
    o_children = 'children'

    # Geometry
    m_position = 'position'
    m_rotation = 'rotRad'
    m_scale = 'scale'
    m_material = 'material'
    m_vis_p = 'visibleInPersonView'
    m_vis_b = 'visibleInBirdView'
    m_vis_f = 'visibleInFloorPlanView'
    v_coords = 'positions'
    v_normals = 'normals'
    uv_coords = 'uvs'
    uv2_coords = 'uvsLightmap'

    # Material
    mat_default = 'al_default'
    col_diff = 'colorDiffuse'
    col_spec = 'colorSpecular'
    coef_spec = 'specularCoef'
    coef_emit = 'lightEmissionCoef'
    opacity = 'opacity'
    # UV1 map size in meters
    uv_scale = 'size'
    # tex_wrap = 'wrap'
    map_diff = 'mapDiffuse'
    map_spec = 'mapSpecular'
    map_norm = 'mapNormal'
    map_alpha = 'mapAlpha'
    map_light = 'mapLight'
    map_suffix_source = 'Source'
    map_suffix_lores = 'Preview'
    map_suffix_hires = ''
    cast_shadows = 'castRealTimeShadows'
    receive_shadows = 'receiveRealTimeShadows'
    # Material Extras
    wf_angle = 'wireframeThresholdAngle'
    wf_thickness = 'wireframeThickness'
    wf_color = 'wireframeColor'
    wf_opacity = 'wireframeOpacity'


    # Baking related material keys
    add_lightmap = 'addLightmap'
    use_in_calc = 'useInBaking'
    hide_after_calc = 'hideAfterBaking'

    # Buffer
    b_coords_offset = 'positionsOffset'
    b_coords_length = 'positionsLength'
    b_normals_offset = 'normalsOffset'
    b_normals_length = 'normalsLength'
    b_uvs_offset = 'uvsOffset'
    b_uvs_length = 'uvsLength'
    b_uvs2_offset = 'uvsLightmapOffset'
    b_uvs2_length = 'uvsLightmapLength'

    #Blender Meta
    bl_meta = 'Data3d Material'
    ...


class Data3dObject(object):
    """
        Attributes:
            node_id ('str') - The nodeId of the object or a generated Id.
            parent ('Data3dObject') -
            children ('list(Data3dObject)') - The children of the D3D Object.
            file_buffer ('bytearray') - The file buffer in memory, if import source is binary.
            payload_byte_offset('int') - The payload byte offset for accessing geometry data.
            materials ('list(dict)') - The object materials as raw json data.
            position ('list(int)') - The relative position of the object.
            rotation ('list(int)') - The relative rotation of the object.
            bl_objects ('list(bpy.types.Object)') - The blender object for this data3d object
            mat_hash_map ('dict') - The HashMap of the object material keys -> blender materials.
            mesh_references('dict') - The mesh keys of the D3D object.
    """

    def __init__(self, node, parent=None, file_buffer=None, payload_byte_offset=0):
        self.node_id = node[D3D.node_id] if D3D.node_id in node else _id_generator(12)
        self.parent = None
        self.children = []
        self.file_buffer = file_buffer
        self.payload_byte_offset = payload_byte_offset

        self.materials = node[D3D.o_materials] if D3D.o_materials in node else []
        self.position = node[D3D.o_position] if D3D.o_position in node else [0, 0, 0]
        self.rotation = node[D3D.o_rotation] if D3D.o_rotation in node else [0, 0, 0]

        self.bl_objects = []
        self.mat_hash_map = {}

        self.mesh_references = node[D3D.o_meshes] if D3D.o_meshes in node else {}

        if parent:
            self.parent = parent
            parent.add_child(self)

    def _get_data3d_mesh_nodes(self, mesh, name):
        """ Return all the relevant nodes of this mesh. Create face data for the mesh import.
            Args:
                mesh ('dict') - The json mesh data.
                name ('str') - The mesh key.
            Returns:
                mesh_data ('dict') - The data of the mesh
        """
        def distinct_coordinates(raw_coords):
            """ Removes duplicate entries from the input. Returns the distincted list and a
                indexed map of the raw input.
                Args:
                    raw_coords ('list') - The raw coordinate list.
                Return:
                    distinct_coords ('list') - The distinct list of coordinates.
                    distinct_indices ('list') - The indices map from raw to distinct coordinates.
            """
            hashed_coords = {}
            distinct_coords = []
            distinct_indices = []
            idx = 0
            for c in raw_coords:
                if c in hashed_coords:
                    distinct_indices.append(int(hashed_coords[c]))
                else:
                    hashed_coords[c] = idx
                    distinct_coords.append(c)
                    distinct_indices.append(idx)
                    idx += 1
            del hashed_coords

            return distinct_coords, distinct_indices

        def from_buffer(m):
            data = {}
            unpacked_coords = self._get_data_from_buffer(m[D3D.b_coords_offset], m[D3D.b_coords_length])
            data['verts_loc_raw'] = [tuple(unpacked_coords[x:x+3]) for x in range(0, len(unpacked_coords), 3)]
            del unpacked_coords

            unpacked_normals = self._get_data_from_buffer(m[D3D.b_normals_offset], m[D3D.b_normals_offset])
            data['verts_nor_raw'] = [tuple(unpacked_normals[x:x+3]) for x in range(0, len(unpacked_normals), 3)]
            del unpacked_normals

            if has_uvs:
                unpacked_uvs = self._get_data_from_buffer(mesh[D3D.b_uvs_offset], mesh[D3D.b_uvs_length])
                data['verts_uvs_raw'] = [tuple(unpacked_uvs[x:x+2]) for x in range(0, len(unpacked_uvs), 2)]
                del unpacked_uvs

            if has_uvs2:
                unpacked_uvs2 = self._get_data_from_buffer(m[D3D.b_uvs2_offset], m[D3D.b_uvs2_length])
                data['verts_uvs2_raw'] = [tuple(unpacked_uvs2[x:x+2]) for x in range(0, len(unpacked_uvs2), 2)]
                del unpacked_uvs2
            return data

        def from_json(m):
            data = {}
            # Vertex location, normal and uv coordinates, referenced by indices
            data['verts_loc_raw'] = [tuple(m[D3D.v_coords][x:x+3]) for x in range(0, len(m[D3D.v_coords]), 3)]
            data['verts_nor_raw'] = [tuple(m[D3D.v_normals][x:x+3]) for x in range(0, len(m[D3D.v_normals]), 3)]

            if has_uvs:
                data['verts_uvs_raw'] = [tuple(m[D3D.uv_coords][x:x+2]) for x in range(0, len(m[D3D.uv_coords]), 2)]
            if has_uvs2:
                data['verts_uvs2_raw'] = [tuple(m[D3D.uv2_coords][x:x+2]) for x in range(0, len(m[D3D.uv2_coords]), 2)]

            return data

        has_uvs = D3D.uv_coords in mesh or D3D.b_uvs_offset in mesh
        has_uvs2 = D3D.uv2_coords in mesh or D3D.b_uvs2_offset in mesh

        # Get mesh data from buffer
        if D3D.b_coords_offset in mesh:
            raw_mesh_data = from_buffer(mesh)

        # Get mesh data from json
        else:
            raw_mesh_data = from_json(mesh)

        # Convert the raw data to mesh_data.
        mesh_data = {
            'name': name,
            'position': mesh[D3D.m_position] if D3D.m_position in mesh else [0, 0, 0],
            'rotation': mesh[D3D.m_rotation] if D3D.m_rotation in mesh else [0, 0, 0],
            'scale': mesh[D3D.m_scale] if D3D.m_scale in mesh else [1, 1, 1]
        }

        if D3D.m_material in mesh:
            mesh_data['material'] = mesh[D3D.m_material]

        mesh_data['verts_loc'], v_indices = distinct_coordinates(raw_mesh_data['verts_loc_raw'])
        face_vertex_indices = [tuple(v_indices[x:x+3]) for x in range(0, len(v_indices), 3)]
        mesh_data['verts_nor'], n_indices = distinct_coordinates(raw_mesh_data['verts_nor_raw'])
        face_normal_indices = [tuple(n_indices[x:x+3]) for x in range(0, len(n_indices), 3)]
        face_uvs_indices = face_uvs2_indices = [(), ] * len(face_vertex_indices)

        if has_uvs:
            mesh_data['verts_uvs'], uvs_indices = distinct_coordinates(raw_mesh_data['verts_uvs_raw'])
            face_uvs_indices = [tuple(uvs_indices[x:x+3]) for x in range(0, len(uvs_indices), 3)]

        if has_uvs2:
            mesh_data['verts_uvs2'], uvs2_indices = distinct_coordinates(raw_mesh_data['verts_uvs2_raw'])
            face_uvs2_indices = [tuple(uvs2_indices[x:x+3]) for x in range(0, len(uvs2_indices), 3)]

        # face = [(loc_idx), (norm_idx), (uv_idx), (uv2_idx)]
        mesh_data['faces'] = [list(f) for f in zip(face_vertex_indices, face_normal_indices, face_uvs_indices, face_uvs2_indices)]

        del raw_mesh_data

        return mesh_data

    def _get_data_from_buffer(self, offset, length):
        """ Returns the specified chunk of the buffer bytearray as a float list.
            Args:
                offset ('int') - The offset of the requested data in the payload.
                length ('int') - The length of the requested data section in the payload.
            Returns:
                data ('list(float)') - The requested data chunk.
        """
        start = self.payload_byte_offset + (offset * 4)
        end = start + (length * 4)
        data = []
        binary_data = self.file_buffer[start:end]
        for x in range(0, len(binary_data), 4):
            data.append(binary_unpack('f', binary_data[x:x+4]))
        return data

    @staticmethod
    def _handle_double_sided_faces(orig_mesh):
        """ Split double sided faces from mesh into a new mesh object
        """
        orig_faces = orig_mesh['faces']
        hashed_faces = {}
        ss_faces = []
        ds_faces = []
        for f in orig_faces:
            v_locs = f[0]
            v_hash = str(sorted(v_locs))
            if v_hash in hashed_faces:
                ds_faces.append(f)
            else:
                ss_faces.append(f)
                hashed_faces[v_hash] = True
        del hashed_faces

        if len(ds_faces) > 0:
            # Fixme: both meshes use the same mesh_data, we only replace the faces -> results in unused points
            # Fixme: implement: split coords per mesh (atm we clean this upon import @optimize_mesh)
            keys = ['name', 'material', 'position', 'rotation', 'scale', 'verts_loc', 'verts_nor', 'verts_uvs', 'verts_uvs2']
            ss_mesh = {key: orig_mesh[key] for key in keys if key in orig_mesh}
            ds_mesh = {key: orig_mesh[key] for key in keys if key in orig_mesh}
            ss_mesh['faces'] = ss_faces
            ds_mesh['faces'] = ds_faces
            return [ss_mesh, ds_mesh]
        else:
            return [orig_mesh]

    def set_bl_object(self, bl_object):
        """ Create a reference to the blender object associated with this Object.
            Args:
                bl_object ('bpy.types.Object') - The blender object.
        """
        self.bl_objects.append(bl_object)


    def add_child(self, child):
        """ Add a child reference to this Object.
            Args:
                child ('Data3dObject')- The child object.
        """
        self.children.append(child)

    def get_mesh_data(self, mesh_key, handle_double_sided=True):
        """ Get the mesh_data for the specified mesh key.
            Args:
                mesh_key ('str') - The mesh key.
            Kwargs:
                handle_double_sided ('bool') - Parse the mesh-data for double sided meshes.
            Returns:
                meshes ('list('dict')') - The list of mesh_data sets. (Mesh is split when double sided)
        """
        if mesh_key in self.mesh_references:
            mesh_data = self._get_data3d_mesh_nodes(self.mesh_references[mesh_key], mesh_key)
            if handle_double_sided:
                meshes = self._handle_double_sided_faces(mesh_data)
            else:
                meshes = [mesh_data]
            return meshes
        else:
            log.error('Mesh key %s not found.', mesh_key)
            return []
        return []


# Temp debugging
def _dump_json_to_file(j, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(j))


# Helper
def _get_data3d_objects_recursive(root, parent=None, file_buffer=None, payload_byte_offset=0):
    """ Go trough the json hierarchy recursively and get all the children.
        Args:
            root ('dict') - The root object to be parsed.
        Kwargs:
            parent ('Data3dObject') - The parent object of the root object.
    """
    recursive_data = []
    children = root[D3D.o_children] if D3D.o_children in root else []
    if children is not []:
        for child in children:
            data3d_object = Data3dObject(child, parent, file_buffer=file_buffer, payload_byte_offset=payload_byte_offset)
            recursive_data.append(data3d_object)
            recursive_data.extend(_get_data3d_objects_recursive(child, data3d_object, file_buffer=file_buffer, payload_byte_offset=payload_byte_offset))
    return recursive_data


def _id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """ Create a random ID from ASCII and digits
        Kwargs:
            size ('int') - The length of the string.
            chars ('str') - Characters to use for random string.
        Returns:
            _ ('str') - The randomly generated string.
    """
    return ''.join(random.choice(chars) for _ in range(size))


def binary_unpack(t, b):
    """ Unpack bytearray data to the specified type.
        Args:
            t ('str') - The data format of the output.
            b ('bytearray') - The bytearray to unpack, the length is dependent on the datatype.
        Returns:
            _ ('t') - The unpacked data.
    """
    return struct.unpack(t, b)[0]


def binary_pack(t, a):
    """ Pack data to a bytearray.
        Args:
            t ('str') - The data format of the input.
            a ('list(t)') - The data to pack.
        Returns:
            _ ('bytearray') - The packed data.
    """
    return struct.pack(t*len(a), *a)


def _py_encode_basestring_ascii(s):
    """ Return an ASCII-only JSON representation of a Python string
        Args:
            s ('str') - The string to encode.
        Returns:
            _ ('str') - The encoded string.
    """
    def replace(match):
        s = match.group(0)
        try:
            return ESCAPE_DCT[s]
        except KeyError:
            n = ord(s)
            if n < 0x10000:
                return '\\u{0:04x}'.format(n)
                #return '\\u%04x' % (n,)
            else:
                # surrogate pair
                n -= 0x10000
                s1 = 0xd800 | ((n >> 10) & 0x3ff)
                s2 = 0xdc00 | (n & 0x3ff)
                return '\\u{0:04x}\\u{1:04x}'.format(s1, s2)

    return '"' + ESCAPE_ASCII.sub(replace, s) + '"'


def _to_json(o, level=0):
    """ Parse python elements into json strings recursively.
        Args:
            o ('any') - The python (sub)element to parse.
            level (int) - The current indent level.
        Returns:
            ret ('str') - The parsed json string.
    """
    json_indent = 4
    json_space = ' '
    json_quote = '"'
    json_newline = '\n'

    ret = ''
    if isinstance(o, dict):
        ret += '{' + json_newline
        comma = ''
        for k, v in o.items():
            ret += comma
            comma = ',' + json_newline
            ret += json_space * json_indent * (level + 1)
            ret += json_quote + str(k) + json_quote + ':' + json_space
            ret += _to_json(v, level+1)
        ret += json_newline + json_space * json_indent * level + '}'
    elif isinstance(o, list):
        ret += '[' + ','.join([_to_json(e, level + 1) for e in o]) + ']'
    elif isinstance(o, str):
        ret += _py_encode_basestring_ascii(o)
    elif isinstance(o, bool):
        ret += 'true' if o else 'false'
    elif isinstance(o, int):
        ret += str(o)
    elif isinstance(o, float):
        if str(o).find('e') != -1:
            ret += '{:.5f}'.format(o)
        else:
            ret += '%.5g' % o
    #elif isinstance(o, numpy.ndarray) ...:
    else:
        raise TypeError("Unknown type '%s' for json serialization" % str(type(o)))

    return ret


def _from_data3d_json(input_path):
    """ Import data3d from data3d.json file.
        Args:
            input_path ('str') - The path to the input file.
        Returns:
            data3d_objects ('list(Data3dObject)') - The deserialized data3d ad Data3dObjects.
            meta ('dict') - The deserialized metadata.
    """

    def read_file_to_json(filepath=''):
        if os.path.exists(filepath):
            data3d_file = open(filepath, mode='r')
            json_str = data3d_file.read()
            return json.loads(json_str)
        else:
            raise Exception('File does not exist, ' + filepath)

    data3d_json = read_file_to_json(filepath=input_path)

    # Import JSON Data3d Objects and add root level object
    root_object = Data3dObject(data3d_json['data3d'])
    data3d_objects = _get_data3d_objects_recursive(data3d_json['data3d'], root_object)
    data3d_objects.append(root_object)

    del data3d_json

    return data3d_objects


def _from_data3d_buffer(input_path):
    """ Import data3d from data3d.buffer file.
        Args:
            input_path ('str') - The path to the input file.
        Returns:
            data3d_objects ('list(Data3dObject)') - The deserialized data3d ad Data3dObjects.
    """

    def read_into_buffer(file_path):
        """ Read binary input file into memory.
            Args:
                file_path ('str') - The input-file.
            Returns:
                buf ('bytearray') - The file-buffer.
        """
        if '.gz' in file_path:
            f = gzip.open(file_path, 'rb')
            buf = bytearray(f.read())
            f.close()
            return buf

        else:
            buf = bytearray(os.path.getsize(file_path))
            with open(file_path, 'rb') as f:
                f.readinto(buf)
            return buf

    def get_header(buffer_file):
        """ Read the header of the data3d.buffer file.
            Args:
                buffer_file ('bytearray') - The buffered data3d file.
            Returns:
                header ('list(int')) - The parsed data3d.buffer header.
        """
        header_array = [buffer_file[x:x+4] for x in range(0, HEADER_BYTE_LENGTH, 4)]
        header = [header_array[0],
                  binary_unpack('i', header_array[1]),
                  binary_unpack('i', header_array[2]),
                  binary_unpack('i', header_array[3])
                  ]
        return header

    file_buffer = read_into_buffer(input_path)

    magic_number, version, structure_byte_length, payload_byte_length = get_header(file_buffer)
    expected_file_byte_length = HEADER_BYTE_LENGTH + structure_byte_length + payload_byte_length

    # Fixme why only != gives accurate result instead of is/is not
    # Validation warnings
    if magic_number != bytearray(MAGIC_NUMBER, 'ascii'):
        log.error('File header error: Wrong magic number. File is probably not data3d buffer format. %s', magic_number)
    if version != VERSION:
        log.error('File header error: Wrong version number: %s. Parser supports version: %s', version, VERSION)

    # Validation errors
    if len(file_buffer) != expected_file_byte_length:
        raise Exception('Can not parse data3d buffer. Wrong buffer size: ' + str(len(file_buffer)) + ' Expected: ' + str(expected_file_byte_length))

    payload_byte_offset = HEADER_BYTE_LENGTH + structure_byte_length
    structure_array = file_buffer[HEADER_BYTE_LENGTH:payload_byte_offset]
    structure_string = structure_array.decode('utf-16')
    structure_json = json.loads(structure_string)

    # Temp
    #_dump_json_to_file(structure_json, dump_file)

    #  Import JSON Data3d Objects and add root level object
    root_object = Data3dObject(structure_json['data3d'], file_buffer=file_buffer, payload_byte_offset=payload_byte_offset)
    data3d_objects = _get_data3d_objects_recursive(structure_json['data3d'], root_object, file_buffer=file_buffer, payload_byte_offset=payload_byte_offset)
    data3d_objects.append(root_object)

    return data3d_objects


def _to_data3d_json(data3d, output_path):
    """ Export data3d to data3d.json file.
        Args:
            data3d ('dict') - The parsed data3d geometry as a dictionary.
            output_path ('str') - The path to the output file.
    """
    # Ensure suffix
    path = output_path
    if not path.endswith(SUFFIX_JSON):
        root = os.path.dirname(path)
        filename = os.path.basename(path).split('.', 1)[0] + '.' + SUFFIX_JSON
        path = '/'.join([root, filename])

    log.debug('Output path: %s', path)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(_to_json(data3d))


def _to_data3d_buffer(data3d, output_path, compress_file):
    """ Export data3d to data3d.buffer file.
        Args:
            data3d ('dict') - The parsed data3d geometry as a dictionary.
            output_path ('str') - The path to the output file.
            compress_file ('bool') - Gzip the output file.
    """
    def create_header(s_length, p_length):
        """ Create the data3d.buffer header from magic number, version and data.
            Args:
                s_length ('int') - The byte length of the structure.
                p_length ('int') - The byte length of the payload.
            Returns:
                _ ('bytearray') - The created header.
        """
        return bytearray(MAGIC_NUMBER, 'ascii') + binary_pack('i', [VERSION, s_length, p_length])

    def extract_buffer_data(d):
        """ Extracts payload data from data3d dict, adds offset & length data to dict.
            Args:
                d ('dict') - The parsed data3d geometry as a dictionary.
            Returns:
                s ('dict') - The modified structure dictionary.
                p ('list(float)') - The payload list of floats.
        """
        s = copy.deepcopy(d)
        p = []

        root = s[D3D.r_container]
        # Flattened Data3d dictionary with no hierarchy
        if D3D.o_meshes in root:
            meshes = root[D3D.o_meshes]
            for mesh_key in meshes:
                mesh = meshes[mesh_key]
                v_loc = mesh.pop(D3D.v_coords, None)
                v_norm = mesh.pop(D3D.v_normals, None)
                v_uvs = mesh.pop(D3D.uv_coords, None)
                v_uvs2 = mesh.pop(D3D.uv2_coords, None)

                mesh[D3D.b_coords_length] = len(v_loc)
                mesh[D3D.b_coords_offset] = len(p)
                p.extend(v_loc)

                mesh[D3D.b_normals_length] = len(v_norm)
                mesh[D3D.b_normals_offset] = len(p)
                p.extend(v_norm)

                if v_uvs:
                    mesh[D3D.b_uvs_length] = len(v_uvs)
                    mesh[D3D.b_uvs_offset] = len(p)
                    p.extend(v_uvs)

                if v_uvs2:
                    mesh[D3D.b_uvs2_length] = len(v_uvs2)
                    mesh[D3D.b_uvs2_offset] = len(p)
                    p.extend(v_uvs2)
        return s, p

    structure, payload = extract_buffer_data(data3d)
    structure_json = json.dumps(structure, indent=None, skipkeys=False)
    structure['version'] = VERSION

    if not len(structure_json) % 2:
        structure_json += ' '

    # Temp
    #_dump_json_to_file(structure, dump_file)

    structure_byte_array = bytearray(structure_json, 'utf-16')
    structure_byte_length = len(structure_byte_array)
    payload_byte_array = binary_pack('f', payload)
    payload_byte_length = len(payload_byte_array)

    header = create_header(structure_byte_length, payload_byte_length)

    # Validation Warnings
    # Validation Errors
    if len(header) != HEADER_BYTE_LENGTH:
        raise Exception('Can not serialize data3d buffer. Wrong header size: ' + str(len(header)) + ' Expected: ' + str(HEADER_BYTE_LENGTH))

    source_name = os.path.basename(output_path)

    if source_name.endswith('.'.join([SUFFIX_GZIP, SUFFIX_BUFFER])):
        filename = '.'.join(source_name.split('.')[:-3])
    else:
        filename = '.'.join(source_name.split('.')[:-2])

    path = os.path.dirname(output_path)

    log.debug('filename %s, pathname %s', filename, path)

    if compress_file:
        filename = '.'.join([filename, SUFFIX_GZIP, SUFFIX_BUFFER])
        with gzip.open('/'.join([path, filename]), 'wb') as buffer_file:
            buffer_file.write(header)
            buffer_file.write(structure_byte_array)
            buffer_file.write(payload_byte_array)
    else:
        filename = '.'.join([filename, SUFFIX_BUFFER])
        with open('/'.join([path, filename]), 'wb') as buffer_file:
            buffer_file.write(header)
            buffer_file.write(structure_byte_array)
            buffer_file.write(payload_byte_array)
    log.info('output_path %s', '/'.join([path, filename]))


# Public functions
def deserialize_data3d(input_path, from_buffer):
    """ Deserialize data3d from .json or .buffer input.
        Args:
            input_path ('str') - The path to the data3d file.
            from_buffer ('bool') - Import format is buffer.
        Returns:
            _ ('list(Data3dObject)') - The deserialized data3d ad Data3dObjects.
    """
    if from_buffer:
        return _from_data3d_buffer(input_path)
    else:
        return _from_data3d_json(input_path)


def serialize_data3d(data3d, output_path, to_buffer):
    """ Serialize data3d to .json or -.buffer file.
        Args:
            data3d ('dict') - The parsed data3d geometry as a dictionary.
            output_path ('str') - The path to the output file.
            to_buffer ('bool') - Export format is buffer.
    """
    if to_buffer:
        _to_data3d_buffer(data3d, output_path, compress_file=True)
    else:
        _to_data3d_json(data3d, output_path)
