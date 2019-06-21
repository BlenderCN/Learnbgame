# GcScannerIconTypes struct

from .Struct import Struct


class GcScannerIconTypes(Struct):
    def __init__(self, **kwargs):
        super(GcScannerIconTypes, self).__init__()

        """ Contents of the struct """
        self.data['ScanIconType'] = kwargs.get('ScanIconType', 'None')
        """ End of the struct contents"""
