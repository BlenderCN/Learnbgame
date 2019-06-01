import re
import math
from mathutils import *

class Mesh:
    def __init__(self, version):
        self.version = version
        self.layers = []
    
    def write_to_file(self, file):
        file.write('SE_MESH {0}\n\n'.format(self.version))
        file.write('LAYERS {0}\n'.format(len(self.layers)) )
        file.write('{\n')
        
        for layer in self.layers:
            layer.write_to_file(file)
        
        file.write('}')

class ASCIIFileQuery:
    def __init__(self, path):
        file = open(path, 'rb')
        
        self.content = file.read()
        self.current_pos = 0
        
        file.close()
    
    def follows_block_begin_decl(self):
        match_obj = re.compile(br"\s*{", re.ASCII).match(self.content, self.current_pos)
        
        if match_obj is None:
            raise RuntimeError("Block not opened")
        
        self.current_pos = match_obj.end()
    
    def follows_block_end_decl(self):
        match_obj = re.compile(br"\s*}", re.ASCII).match(self.content, self.current_pos)
        
        if match_obj is None:
            raise RuntimeError("Block not closed")
        
        self.current_pos = match_obj.end()
    
    def get_map_type(self, is_vertex = True):
        if is_vertex:
            map_str = "VERTEX_MAP"
            get_type_const = VertexMap.get_type_const
        else:
            map_str = "POLYGON_MAP_NAME"
            get_type_const = PolygonMap.get_type_const
        
        reg_exp = "\s+{0}\s*\"([^\.\n]*)\.".format(map_str).encode('ascii')
        
        match_obj = re.compile(reg_exp, re.ASCII).match(self.content, self.current_pos)
        
        if match_obj:
            map_type = get_type_const(str(match_obj.group(1), 'ascii'))
        else:
            raise RuntimeError("Can't find map type declaration")
        
        if map_type is None:
            raise RuntimeError("Unsupported map type")
        
        self.current_pos = match_obj.end()
        
        return map_type
    
    def get_map_name(self):
        match_obj = re.compile(br"(.*)\"\s*", re.ASCII).match(self.content, self.current_pos)
        
        if match_obj:
            map_name = str(match_obj.group(1), 'ascii')
        else:
            raise RuntimeError("Can't find map name declaration")
        
        self.current_pos = match_obj.end()
        
        return map_name
    
    def get_morph_elem(self):
        elem_data = r"([+-]?[\deE]+(?!\.)|[+-]?\d+\.*[\deE]+[eE]?[+-]?\d*)"

        reg_exp = r"\s*{0}\s*,\s*{0}\s*,\s*{0}\s*;".format(elem_data).encode('ascii')

        match_obj = re.compile(reg_exp, re.ASCII).match(self.content, self.current_pos)

        if match_obj:
            elems = (float(match_obj.group(1)), float(match_obj.group(2)), float(match_obj.group(3)))
        else:
            raise RuntimeError("Can't find vertex map element declatation")
        
        self.current_pos = match_obj.end()
        
        return elems
    
    def get_texcoord_elem(self):
        elem_data = r"([+-]?[\deE]+(?!\.)|[+-]?\d+\.*[\deE]+[eE]?[+-]?\d*)"
        
        reg_exp = r"\s*{0}\s*,\s*{0}\s*;".format(elem_data).encode('ascii')
        
        match_obj = re.compile(reg_exp, re.ASCII).match(self.content, self.current_pos)
        
        if match_obj is not None:
            elems = (float(match_obj.group(1)), float(match_obj.group(2)))
        else:
            raise RuntimeError("Can't find vertex map elements declaration")
        
        self.current_pos = match_obj.end()
        
        return elems

    def get_weight_elem(self):
        elem_data = r"(\d*(?!\.)|\d+.\d+[eE]*[+-]*\d*)"
        
        reg_exp = r"\s*{0}\s*;".format(elem_data).encode('ascii')
        
        match_obj = re.compile(reg_exp, re.ASCII).match(self.content, self.current_pos)
        
        if match_obj is not None:
            elems = float(match_obj.group(1))
        else:
            raise RuntimeError("Can't find vertex map elements declaration")
        
        self.current_pos = match_obj.end()
        
        return elems
    
    def get_num_of_values(self):
        match_obj = re.compile(br"\s*(\d+)\s*:", re.ASCII).match(self.content, self.current_pos)
        
        if match_obj:
            num_of_values = int(match_obj.group(1))
        else:
            raise RuntimeError("Can't find number of values")
        
        self.current_pos = match_obj.end()
        
        return num_of_values
    
    def get_vertex_data_pointer(self, is_last_pointer):
        re_data = br"\s*(\d+)\[(\d+)\]"
        
        if is_last_pointer:
            reg_exp = re_data + br"\s*;"
        else:
            reg_exp = re_data + br"\s*,"
            
        match_obj = re.compile(reg_exp, re.ASCII).match(self.content, self.current_pos)
        
        if match_obj:
            pointer = (int(match_obj.group(1)), int(match_obj.group(2)))
        else:
            raise RuntimeError("Can't find vertex data pointer!")
        
        self.current_pos = match_obj.end()
        
        return pointer
    
    def get_vert_idx(self, is_last_data):
        re_data = br"\s*(\d+)"
        
        if is_last_data:
            reg_exp = re_data + br"\s*;"
        else:
            reg_exp = re_data + br"\s*,"
            
        match_obj = re.compile(reg_exp, re.ASCII).match(self.content, self.current_pos)
        
        if match_obj:
            vert_idx = int(match_obj.group(1))
        else:
            raise RuntimeError("Can't find vertex index")
        
        self.current_pos = match_obj.end()
        
        return vert_idx
        
    def get_long_value(self, ident):
        reg_exp = "\s*{0}\s+(\d+)".format(ident).encode('ascii')
        
        match_obj = re.compile(reg_exp, re.ASCII).match(self.content, self.current_pos)
        
        if match_obj:
            long_value = int(match_obj.group(1))
        else:
            raise RuntimeError("Can't find long value")
        
        self.current_pos = match_obj.end()
        
        return long_value
        
    def get_num_value(self, ident):
        reg_exp = "\s*{0}\s+([+-]?\d+(?!\.)|[+-]?\d+\.\d+[eE]?[+-]?\d*)".format(ident).encode('ascii')
        
        match_obj = re.compile(reg_exp, re.ASCII).match(self.content, self.current_pos)
        
        if match_obj:
            num_value = float(match_obj.group(1))
        else:
            raise RuntimeError("Can't find number value")
        
        self.current_pos = match_obj.end()
        
        return num_value

    def get_str_value(self, ident):
        reg_exp = "\s+{0}\s+\"(.*)\"".format(ident).encode('ascii')
        
        match_obj = re.compile(reg_exp, re.ASCII).match(self.content, self.current_pos)
        
        if match_obj:
            str_value = str(match_obj.group(1), 'ascii')
        else:
            raise RuntimeError("Can't find string value")
        
        self.current_pos = match_obj.end()
        
        return str_value
    
    def get_bool_value(self, ident):
        reg_exp = "\s+{0}\s+(TRUE|FALSE)".format(ident).encode('ascii')
        
        match_obj = re.compile(reg_exp, re.ASCII).match(self.content, self.current_pos)
        
        if match_obj:
            bool_value = str(match_obj.group(1), 'ascii') == "TRUE"
        else:
            return None
        
        self.current_pos = match_obj.end()
        
        return bool_value
    
    def get_poly_idx(self):
        match_obj = re.compile(br"\s*(\d+)\s*;", re.ASCII).match(self.content, self.current_pos)
        
        if match_obj:
            poly_idx = int(match_obj.group(1))
        else:
            raise RuntimeError("Can't find polygon index")
        
        self.current_pos = match_obj.end()
        
        return poly_idx

class Layer:
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.basic_morph_map = None
        self.non_basic_morph_maps = []
        self.weight_maps = []
        self.texcoord_maps = []
        self.vertex_maps = []
        self.vertices = []
        self.polygons = []
        self.surface_maps = []
        self.polygon_maps = []
    
    def vertex_maps_append(self, vertex_map):
        type = vertex_map.type
        
        if type == VERTEX_MAP_TYPE_MORPH:
            if self.basic_morph_map:
                self.non_basic_morph_maps.append(vertex_map)
            else:
                self.basic_morph_map = vertex_map
        elif type == VERTEX_MAP_TYPE_WEIGHT:
            self.weight_maps.append(vertex_map)
        elif type == VERTEX_MAP_TYPE_TEXCOORD:
            self.texcoord_maps.append(vertex_map)
        
        self.vertex_maps.append(vertex_map)
    
    def write_to_file(self, file):
        file.write('  ')
        file.write('LAYER_NAME "{0}"\n'.format(self.name))
        file.write('  ')
        file.write('LAYER_INDEX {0}\n'.format(self.index))
        file.write('  {\n')
        file.write('')
        
        file.write('    ')
        file.write('VERTEX_MAPS {0}\n'.format( len(self.vertex_maps) ))
        file.write('    {\n')
        
        for vertex_map in self.vertex_maps:
            vertex_map.write_to_file(file)
        
        file.write('    }\n    \n')
        
        file.write('    ')
        file.write('VERTICES {0}\n'.format( len(self.vertices) ))
        file.write('    {\n')
        
        for vert in self.vertices:
            vert.write_to_file(file)
        
        file.write('    }\n    \n')
        
        file.write('    ')
        file.write('POLYGONS {0}\n'.format(len(self.polygons) ) )
        file.write('    {\n')
        
        for poly in self.polygons:
            file.write('      ')
            
            file.write('{{ {0}: '.format(len(poly) ))
            
            for elem in poly:
                file.write(str(elem))
                
                if poly.index(elem) + 1 < len(poly):
                    file.write(', ')
            
            file.write('; }\n')
        
        file.write('    }\n    \n')
        
        file.write('    ')
        file.write('POLYGON_MAPS {0}\n'.format(len(self.polygon_maps) ))
        file.write('    {\n')
        
        for poly_map in self.polygon_maps:
            poly_map.write_to_file(file)
        
        file.write('    }\n')
        file.write('  }\n')

VERTEX_MAP_TYPE_MORPH = 0
VERTEX_MAP_TYPE_WEIGHT = 1
VERTEX_MAP_TYPE_TEXCOORD = 2

class VertexMap:
    def __init__(self, type, name, relative = None):
        self.type = type
        self.name = name
        
        self.type_index = 0
        
        if self.type == VERTEX_MAP_TYPE_MORPH:
            if re.match('position', name, re.IGNORECASE):
                self.is_basic = True
                self.relative = False if relative is None else relative
            else:
                self.is_basic = False
                self.relative = True if relative is None else relative
        
        self.elements = []
    
    def get_type_string(self):
        if self.type == VERTEX_MAP_TYPE_MORPH:
            return 'morph'
        elif self.type == VERTEX_MAP_TYPE_WEIGHT:
            return 'weight'
        elif self.type == VERTEX_MAP_TYPE_TEXCOORD:
            return 'texcoord'
    
    @classmethod
    def get_type_const(cls, type_str):
        if type_str == "morph":
            return VERTEX_MAP_TYPE_MORPH
        elif type_str == "weight":
            return VERTEX_MAP_TYPE_WEIGHT
        elif type_str == "texcoord":
            return VERTEX_MAP_TYPE_TEXCOORD
        
        return None
    
    def write_to_file(self, file):
        type_str = self.get_type_string()
        name = self.name
        elems = self.elements
        elems_count = len(self.elements)
        
        weight_str = '{{ {0:G}; }}'
        morph_str = '{{ {0[0]:G}, {0[1]:G}, {0[2]:G}; }}'
        texcoord_str = '{{ {0[0]:G}, {0[1]:G}; }}'
        
        if self.type == VERTEX_MAP_TYPE_MORPH:
            format_str = morph_str
        elif self.type == VERTEX_MAP_TYPE_WEIGHT:
            format_str = weight_str
        elif self.type == VERTEX_MAP_TYPE_TEXCOORD:
            format_str = texcoord_str
        
        file.write('      ')
        file.write('VERTEX_MAP "{0}.{1}"\n'.format(type_str, name))
        file.write('      {\n')
        
        if self.type == VERTEX_MAP_TYPE_MORPH:
            file.write('        ')
            file.write('RELATIVE {0}\n'.format('TRUE' if self.relative else 'FALSE') )
        
        file.write('        ')
        file.write('ELEMENTS {0}\n'.format(elems_count))
        file.write('        {\n')
        
        for elem in elems:
            file.write('          ')
            file.write(format_str.format(elem))
            file.write('\n')
        
        file.write('        }\n')
        file.write('      }\n')

class Vertex:
    def __init__(self, index=None):
        self.index = index
        self.morph_pointers = []
        self.weight_pointers = []
        self.uv_pointers = []
    
    @property
    def basic_morph_pointer(self):
        return self.morph_pointers[0]
        
    @property
    def non_basic_morph_pointers(self):
        pointers = self.morph_pointers
        last_pointer_index = len(pointers)
        return pointers[1:last_pointer_index]
    
    @property
    def unique_pointers(self):
        pointers = list(self.morph_pointers)
        pointers.extend(self.weight_pointers)
        return pointers
    
    @property
    def elements(self):
        elements = list(self.unique_pointers)
        elements.extend(self.uv_pointers)
        return elements
    
    def set_unique_pointers_from(self, se3_first_vertex):
        self.morph_pointers = se3_first_vertex.morph_pointers
        self.weight_pointers = se3_first_vertex.weight_pointers
    
    def write_to_file(self, file):
        elems = self.elements
        elems_count = len(elems)
        
        file.write('      {{ {0}: '.format(elems_count))
        
        for elem in elems:
            file.write( '{0}[{1}]'.format(elem[0], elem[1] )  )
            
            if elems.index(elem) + 1 < elems_count:
                file.write(', ')
        
        file.write('; }\n')

class UvVertex:
    def __init__(self, uv, map_element_index, vertex_index, map_index):
        self.uv = uv
        self.map_element_index = map_element_index
        self.vertex_index = vertex_index
        self.map_index = map_index

class UvVertices:
    def __init__(self):
        self.verticesList = []
    
    def append(self, vertex):
        self.verticesList.append(vertex)
        
    def get_vertex_with(self, uv):
        for uv_vertex in self.verticesList:
            if uv_vertex.uv == uv:
                return uv_vertex
        return None

class BuildingVertex:
    def __init__(self, num_of_texcoord_maps):
        self.final_vertices = []
        self.uv_vertices = [UvVertices()] * num_of_texcoord_maps
    
    def get_vertex_index_with(self, se3_uv_pointers):
        for vertex in self.final_vertices:
            if vertex.uv_pointers == se3_uv_pointers:
                return vertex.index
        return None
    
    @property
    def first_vertex(self):
        return self.final_vertices[0]

POLYGON_MAP_TYPE_SURFACE = 0

class PolygonMap:
    def __init__(self, type, name, smoothing_angle):
        self.type = type
        self.name = name
        self.smoothing_angle = smoothing_angle
        self.polygons = []
        
    def get_type_string(self):
        if self.type == POLYGON_MAP_TYPE_SURFACE:
            return 'surface'
    
    @classmethod
    def get_type_const(cls, type_str):
        if type_str == "surface":
            return POLYGON_MAP_TYPE_SURFACE
        
        return None
    
    def write_to_file(self, file):
        type = self.get_type_string()
        name = self.name
        smooth_angle = self.smoothing_angle
        polys = self.polygons
        
        file.write('      ')
        file.write('POLYGON_MAP_NAME "{0}.{1}"\n'.format(type, name))
        file.write('      ')
        file.write('POLYGON_MAP_SMOOTHING_ANGLE {0}\n'.format(smooth_angle))
        file.write('      ')
        
        file.write('POLYGONS_COUNT {0}\n'.format(len(self.polygons)  ))
        file.write('      {\n')
        
        for poly in polys:
            file.write('        ')
            file.write(str(poly))
            file.write(';\n')
        
        file.write('      }\n')

class Animation:
    def __init__(self, version, name, second_per_frame, first_frame,
                 last_frame):
        self.version = version
        self.name = name
        self.second_per_frame = second_per_frame
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.envelopes = []
        
    def write_to_file(self, file):
        file.write('SE_ANIMATION {}\n\n'.format(self.version))
        file.write('ANIMATION_NAME "{0}"\n'.format(self.name))
        file.write('SEC_PER_FRAME {0}\n'.format(self.second_per_frame))
        file.write('FIRST_FRAME {0}\n'.format(self.first_frame) )
        file.write('LAST_FRAME {0}\n\n'.format(self.last_frame) )
        
        
        file.write('ENVELOPES {0} {{\n'.format(len(self.envelopes)) )
        
        for envelope in self.envelopes:
            envelope.write_to_file(file)
        
        file.write('}')

class Envelope:
    def __init__(self, name):
        self.name = name
        self.channels = []
    
    def write_to_file(self, file):
        file.write('  ENVELOPE "{0}" {{\n'.format(self.name) )
        file.write('    CHANNELS {0} {{\n'.format( len(self.channels)  )  )
        
        for channel in self.channels:
            channel.write_to_file(file)
        
        file.write('    }\n')
        file.write('  }\n')

class Channel:
    def __init__(self, name, default = None):
        self.name = name
        self.default = default
        self.frames = []
    
    def write_to_file(self, file):
        file.write('      CHANNEL "{0}";\n'.format(self.name) )
        file.write('      DEFAULT: {0};\n'.format(self.default) )
        file.write('      FRAMES {0} {{\n'.format(len(self.frames)) )
        
        for frame in self.frames:
            file.write('        {0[0]}: {0[1]};\n'.format(frame) )
        
        file.write('      }\n')

def to_child_rotation_matrix(m):
    return Matrix((( m[0][0],  m[0][2], -m[0][1]),
                   ( m[2][0],  m[2][2], -m[2][1]),
                   (-m[1][0], -m[1][2],  m[1][1])))
                   
def to_free_rotation_matrix(m):
    return Matrix(((-m[0][0], -m[1][0],  m[2][0]),
                   ( m[0][1],  m[1][1], -m[2][1]),
                   ( m[0][2],  m[1][2], -m[2][2])))

def matrix_to_euler(m):
    return (math.atan2(m[0][2], m[2][2]), math.asin(-m[1][2]),
            math.atan2(m[1][0], m[1][1]))

def to_child_position(loc, parent_length):
    return (loc[0], loc[2], -(parent_length + loc[1]))

def to_free_position(loc):
    return (-loc[0], loc[2], loc[1])