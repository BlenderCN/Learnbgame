"""
 Parser for entity component c++ header files.
"""

import os
import struct

def get_hash(name):
    """
    Get the tundra hash for a name.
    """
    # from tundra:Core:CoreStringUtils.cpp:GetHash()
    ret = 0
    if not name:
        return ret
    name_b = name.lower().encode('utf-8')
    for c in name_b:
        ret = (struct.unpack('<B', c)[0] + (ret<<6) + (ret<<16) - ret) & 0xFFFFFFFF
    return ret


class ComponentData(object):
    """
    Component data
    """
    def __init__(self, tpl, data=None):
        self._tpl = tpl
        if data:
            self.initialize(data)

    def initialize(self, data):
        """
        Initialize with given data.
        """
        attrs_size = data.get_u8()
        data.fill(120)
        if not attrs_size == len(self._tpl.attribute_names):
            print("Different sizes!", self._tpl.component_name, attrs_size,
                                            len(self._tpl.attribute_names))
        for idx, name in enumerate(self._tpl.attribute_names):
            attrtype = self._tpl.attributes[name]
            val = None
            if attrtype == 'vector3':
                val = data.get_vector3()
            elif attrtype == 'vector4':
                val = data.get_vector4()
            elif attrtype == 'transform':
                val = data.get_transform()
            elif attrtype == 'string':
                val = data.get_string(16)
            elif attrtype == 'boolean':
                val = data.get_bool()
            elif attrtype == 'float':
                val = data.get_float()
            elif attrtype == 'integer':
                val = data.get_s32()
            elif attrtype == 'uint':
                val = data.get_u32()
            elif attrtype == 'asset':
                val = data.get_string(8)
            elif attrtype == 'assetlist':
                val = data.get_string_list(8, 8)
            if val == None:
                print(name, 'with no value!!', attrtype)
            else:
                setattr(self, name, val)

    def __str__(self):
        """
        Return a string representation of the object.
        """
        return "ComponentData(%s) [%s]" % (self._tpl.component_name,
                                           self.__dict__)

class ComponentTemplate(object):
    """
    A component template.
    """
    def __init__(self, name):
        self.component_name = name
        self.attributes = {}
        self.attribute_names = []

    def add_attribute(self, name, attribute):
        """
        Add an attribute to this template.
        """
        self.attributes[name] = attribute
        self.attribute_names.append(name)

    def deserialize(self, data):
        """
        Deserialize a component from the given data.
        """
        cdata = ComponentData(self, data)
        return cdata

    def __str__(self):
        return "ComponentTemplate(%s) [%s attributes]" % (self.component_name,
                                                          self.attributes)

type_map = {'QVector3D': 'vector3',
            'Vector3df': 'vector3',
            'Color': 'vector4', # XXX ?
            'Transform': 'transform',
            'bool': 'boolean',
            'QString': 'string',
            'float': 'float',
            'int': 'integer',
            'uint': 'uint',
            'AssetReference' : 'asset',
            'AssetReferenceList' : 'assetlist'}

class ECParser(object):
    """
    Entity component c++ header parser.
    """
    def __init__(self):
        self._components = {}
        self._components['unknown'] = ComponentTemplate('unknown')
        self._comp2hash = {}

    def deserialize(self, namehash, data):
        """
        Deserialize the given data using the template for the component
        with the given namehash.
        """
        try:
            name = self._comp2hash[namehash]
        except:
            name = 'unknown'
        c = self.get_component(name)
        return c.deserialize(data)

    def get_component(self, name):
        """
        Get the component with the given name.
        """
        return self._components[name]

    def has_component(self, name):
        """
        Check if the parser has the component with the given
        name.
        """
        return name in self._components

    def parse_file(self, filename):
        """
        Parse the given file looking for entity components.
        """
        f = open(filename, 'r')
        data = f.readlines()
        f.close
        c = None
        for line in data:
            line = line.strip()
            if line.startswith('class') and 'IComponent' in line:
                c = self.parse_component_line(line)
            elif line.startswith('Attribute<'):
                c.add_attribute(*self.parse_attribute_line(line))
            elif line.startswith('DEFINE_QPROPERTY_ATTRIBUTE'):
                c.add_attribute(*self.parse_define_line(line))
        if c:
            self._components[c.component_name] = c
            self._comp2hash[get_hash(c.component_name)] = c.component_name

    def parse_component_line(self, line):
        """
        Parse a component class declaration line.
        """
        name = line.split(':')[0].strip().split(' ')[-1]
        return ComponentTemplate(name)

    def parse_attribute_line(self, line):
        """
        Parse a line containing a single attribute declared by using
        a template.
        """
        name = line.split(' ')[1].strip(';')
        proptype = line.split('>')[0].split('<')[1]
        return name, type_map.get(proptype, proptype)

    def parse_define_line(self, line):
        """
        Parse a line containing a single attribute declared by using
        a macro.
        """
        values = line.split('(')[1].split(')')[0]
        proptype, name = values.split(',')
        proptype = proptype.strip()
        return name.strip(), type_map.get(proptype, proptype)

    def add_dir(self, dirname):
        """
        Scan the given directory recursively looking for c++ header
        files and entity components inside.
        """
        for dirpath, dirnames, filenames in os.walk(dirname):
            for filename in filenames:
                full_filename = os.path.join(dirpath, filename)
                if filename.startswith('EC_') and filename.endswith('.h'):
                    self.parse_file(full_filename)

if __name__ == '__main__':
    p = ECParser()
    p.add_dir('/home/caedes/SVN/REALXTEND/tundra')
    for c in p._components.values():
        print(c)
