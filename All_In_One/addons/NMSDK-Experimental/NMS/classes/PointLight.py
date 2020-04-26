# Custom TkSceneNodeData struct for PointLights

from .List import List
from .TkSceneNodeAttributeData import TkSceneNodeAttributeData
from .TkTransformData import TkTransformData


class PointLight():
    def __init__(self, **kwargs):

        # Attribute properties
        self.FOV = kwargs.get('FOV', 360.0)
        self.Falloff = kwargs.get('Falloff', 'quadratic')
        self.Intensity = kwargs.get('Intensity', 10000.0)
        self.Colour = kwargs.get('Colour', (1, 1, 1))     # RBG colour

        # Scene node properties
        self.Name = kwargs.get('Name', 'pointlight')
        self.Transform = kwargs.get(
            'Transform',
            TkTransformData(TransX=0, TransY=0, TransZ=0,
                            RotX=0, RotY=0, RotZ=0,
                            ScaleX=1, ScaleY=1, ScaleZ=1))

        self.Type = "LIGHT"

    def process_attributes(self):
        self.Attributes = List()
        self.Attributes.append(TkSceneNodeAttributeData(Name="FOV",
                                                        Value=self.FOV))
        self.Attributes.append(TkSceneNodeAttributeData(Name="FALLOFF",
                                                        Value=self.Falloff))
        self.Attributes.append(TkSceneNodeAttributeData(Name="INTENSITY",
                                                        Value=self.Intensity))
        self.Attributes.append(TkSceneNodeAttributeData(Name="COL_R",
                                                        Value=self.Colour[0]))
        self.Attributes.append(TkSceneNodeAttributeData(Name="COL_G",
                                                        Value=self.Colour[1]))
        self.Attributes.append(TkSceneNodeAttributeData(Name="COL_B",
                                                        Value=self.Colour[2]))
        self.Attributes.append(TkSceneNodeAttributeData(
            Name="MATERIAL",
            Value="MATERIALS/LIGHT.MATERIAL.MBIN"))
