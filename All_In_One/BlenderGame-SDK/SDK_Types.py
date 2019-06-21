import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       FloatVectorProperty,
                       IntVectorProperty,
                       BoolVectorProperty,
                       CollectionProperty,)
                       
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       Property,)

class bcolors:
    HEADER      = "\033[95m"
    OKBLUE      = "\033[94m"
    OKGREEN     = "\033[92m"
    WARNING     = "\033[93m"
    FAIL        = "\033[91m"
    ENDC        = "\033[0m"
    BOLD        = "\033[1m"
    UNDERLINE   = "\033[4m"

class InstallMod:
    LOCAL = 0x0
    USER  = 0x1
    
class Module:
    
    def __init__(self):
        
        pass
        
class DrawStack:

    def __init__(self):
        self.__elements = []

    def addElement(self, element, id=-1):
        
        if callable(element):
            self.__elements.insert(id, element)

    def popElement(self, element):
        
        if isinstance(element, int):
            del self.__elements[element]
        elif callable(element):
            self.elemnts.remove(element)

    def moveElement(self, element, new_index):
        
        if isinstance(new_index, int) and 0 <= new_index < len(self.__elements):
            
            if isinstance(element, int):
                if 0 <= element < len(self.__elements):
                    tmp = self.__elements[element]
                    self.__elements[element] = self.__elements[new_index]
                    self.__elements[new_index] = tmp

            elif callable(element):
                id = self.__elements.index(element)
                tmp = self.__elements[id]
                self.__elements[id] = self.__elements[new_index]
                self.__elements[new_index] = tmp

    def draw(self, context):
        
        for i in self.__elements:
            i(self, context)

SE_LABEL_NAME = 0b01
SE_CLASS_NAME = 0b10