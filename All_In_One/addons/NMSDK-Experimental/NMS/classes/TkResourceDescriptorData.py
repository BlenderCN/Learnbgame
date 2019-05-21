# TkResourceDescriptorData struct

from .Struct import Struct
from .List import List
from .String import String


class TkResourceDescriptorData(Struct):
    def __init__(self, **kwargs):
        super(TkResourceDescriptorData, self).__init__()

        """ Contents of the struct """
        self.data['Id'] = String(kwargs.get('Id', "_PROCOBJ_"), 0x10)
        self.data['Name'] = String(kwargs.get('Name', "_PROCOBJ_"), 0x80)
        self.data['ReferencePaths'] = kwargs.get("ReferencePaths", List())
        self.data['Chance'] = kwargs.get("Chance", 0)
        self.data['Children'] = kwargs.get("Children", List())
        """ End of the struct contents"""
