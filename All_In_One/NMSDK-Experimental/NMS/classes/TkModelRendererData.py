# TkModelRendererData struct

from .Struct import Struct
from .TkModelRendererCameraData import TkModelRendererCameraData


class TkModelRendererData(Struct):
    def __init__(self, **kwargs):
        super(TkModelRendererData, self).__init__()

        """ Contents of the struct """
        self.data['Camera'] = kwargs.get('Camera', TkModelRendererCameraData())
        self.data['Fov'] = kwargs.get('Fov', 30)
        self.data['AspectRatio'] = kwargs.get('AspectRatio', 1.7777)
        self.data['ThumbnailMode'] = kwargs.get('ThumbnailMode', "None")
        self.data['FocusType'] = kwargs.get('FocusType', "ResourceBounds")
        self.data['Anim'] = kwargs.get('Anim', "")
        self.data['HeightOffset'] = kwargs.get('HeightOffset', 0.005)
        """ End of the struct contents"""
