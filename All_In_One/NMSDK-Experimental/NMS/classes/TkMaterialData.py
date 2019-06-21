# TkMaterialData struct

from .Struct import Struct
from .List import List
from .TkMaterialFlags import TkMaterialFlags
from .TkMaterialUniform import TkMaterialUniform
from .Vector4f import Vector4f
from .String import String


class TkMaterialData(Struct):
    def __init__(self, **kwargs):
        super(TkMaterialData, self).__init__()

        """ Contents of the struct """
        self.data['Name'] = String(kwargs.get('Name', ""), 0x80)
        self.data['Class'] = String(kwargs.get('Class', "Opaque"), 0x20)
        self.data['TransparencyLayerID'] = kwargs.get('TransparencyLayerID', 0)
        self.data['CastShadow'] = kwargs.get('CastShadow', "False")
        self.data['DisableZTest'] = kwargs.get('DisableZTest', "False")
        self.data['Link'] = String(kwargs.get('Link', ""), 0x80)
        self.data['Shader'] = String(
            kwargs.get('Shader', "SHADERS/UBERSHADER.SHADER.BIN"), 0x80)
        self.data['Flags'] = kwargs.get('Flags', List(TkMaterialFlags()))
        self.data['Uniforms'] = kwargs.get(
            'Uniforms',
            List(
                TkMaterialUniform(
                    Name="gMaterialColourVec4",
                    Values=Vector4f(x=1.0, y=1.0, z=1.0, t=1.0)),
                TkMaterialUniform(
                    Name="gMaterialParamsVec4",
                    Values=Vector4f(x=0.9, y=0.5, z=0.0, t=0.0)),
                TkMaterialUniform(
                    Name="gMaterialSFXVec4",
                    Values=Vector4f()),
                TkMaterialUniform(
                    Name="gMaterialSFXColVec4",
                    Values=Vector4f())))
        self.data['Samplers'] = kwargs.get('Samplers', None)
        """ End of the struct contents"""
