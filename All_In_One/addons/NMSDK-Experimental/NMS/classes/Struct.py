# Base struct class

# stdlib imports
from xml.etree.ElementTree import SubElement, Element, ElementTree
from numbers import Number
from array import array
from collections import OrderedDict
import struct
from binascii import hexlify
# internal imports
from .String import String
from ...serialization.utils import to_chr
from .Empty import Empty
from .List import List


class Struct():
    def __init__(self, **kwargs):
        # by having this as an ordered dict, we get stuff in their order of
        # creation which is crucial for writing directly to an mbin
        self.data = OrderedDict()
        self.parent = None

# region public methods

    def make_elements(self, name=None, main=False):
        # creates a sub element tree that is to be returned or read by the
        # parent class.
        # the optional 'main' argument is a boolean value that is almost
        # always False.
        # In the case of it being true, the SubElement is the primary one, and
        # needs a 'Data' tag, not a 'Property' tag

        # if a name is given then the struct is a single sub element.
        # If no name is given then the sub element must be in a list and give
        # it no name as the name is in the list
        if main is False:
            if name is not None:
                self.element = SubElement(
                    self.parent,
                    'Property',
                    {'name': name, 'value': self.name + '.xml'})
            else:
                self.element = SubElement(
                    self.parent,
                    'Property',
                    {'value': self.name + '.xml'})
        else:
            # in this case, we expect the name to be specified.
            # parent can be None in this case as it is is the main element
            self.element = Element('Data', {'template': self.name})
            self.tree = ElementTree(self.element)

        # iterate through all the data and determine type and sort it out
        # appropriately
        for pname in self.data:
            data = self.data[pname]
            if isinstance(data, Number):
                # in this case convert the int or foat to a string
                SubElement(
                    self.element,
                    'Property',
                    {'name': pname, 'value': str(data)})
            elif isinstance(data, String):
                # in this case we just add the string value as normal
                SubElement(
                    self.element,
                    'Property',
                    {'name': pname, 'value': str(data.string)})
            elif isinstance(data, Empty):
                pass
            elif isinstance(data, str):
                # in this case we just add the string value as normal
                SubElement(
                    self.element,
                    'Property',
                    {'name': pname, 'value': data})
            elif isinstance(data, list):
                # In this case we need to add each element of the list as a
                # sub property.
                # first add the name as a SubElement
                SE = SubElement(self.element, 'Property', {'name': pname})
                for i in data:
                    SubElement(SE, 'Property', {'value': str(i)})
            elif isinstance(data, array):
                SE = SubElement(self.element, 'Property', {'name': pname})
                for i in data:
                    SubElement(SE, 'Property', {'value': str(i)})
            elif data is None:
                SubElement(self.element, 'Property', {'name': pname})
            else:
                # Only other option is for it to be a class object.
                # This will be a class object itself.
                data.give_parent(self.element)
                data.make_elements(pname)

    def give_parent(self, parent):
        self.parent = parent

    def serialize(self, output, list_worker, return_data=False):
        # serialize all the data...
        serialized_data = ""
        for key in self.data:
            data = self.data[key]
            if isinstance(data, array) or isinstance(data, list):
                data = List(*list(data))
            # check whether the object has a serialize function
            if hasattr(data, 'serialize'):
                data.serialize(output, list_worker, return_data)
            else:
                if type(data) == int:
                    serialized_data = to_chr(hexlify(struct.pack('<i', data)))
                    list_worker['curr'] += 0x4
                elif type(data) == float:
                    serialized_data = to_chr(hexlify(struct.pack('<f', data)))
                    list_worker['curr'] += 0x4
                elif type(data) == bool:
                    serialized_data = chr(data)
                    list_worker['curr'] += 0x1
                elif type(data) == str:
                    try:
                        # in this case we actually want the index
                        val = self.__dict__[key].index(data)
                        serialized_data = to_chr(hexlify(struct.pack(
                            '<i', val)))
                        list_worker['curr'] += 0x4
                    except IndexError:
                        serialized_data = to_chr('FFFFFFFF')
                        list_worker['curr'] += 0x4
                if return_data is False:
                    output.write(serialized_data)
                    msg = ('serialized {0}, with value {1}, ending at {2:#x}. '
                           ' File end = {3:#x}')
                    print(msg.format(key, data, list_worker['curr'],
                                     list_worker['end']))
        if return_data is True:
            return serialized_data

# region properties

    @property
    def name(self):
        return self.__class__.__name__

# region class methods

    def __getitem__(self, key):
        # returns the object in self.data with key
        return self.data[key]

    def __setitem__(self, key, value):
        # assigns the value 'value' to self.data[key]
        # currently no checking so be careful! Incorrect use could lead to
        # incorrect exml files!!!
        self.data[key] = value

    def __str__(self):
        return "Name: {0}".format(self.name)

    def __len__(self):
        # returns the length of the Struct in bytes. Works better when
        # everything has values other than None by default.
        length = 0
        for key in self.data:
            val = self.data[key]
            # if it is an int or a float the size will be 4 bytes
            if type(val) == int or type(val) == float:
                length += 0x4
            elif type(val) == bool:
                length += 0x1
            else:
                # we can also see if the value has a length attribute (such as
                # for NMSString0x80)
                try:
                    length += val.size
                # otherwise just try call this function recursively
                except AttributeError:
                    length += len(val)
        return length
