# GcScannableComponentData struct

from .Struct import Struct
from .GcScannerIconTypes import GcScannerIconTypes


class GcScannableComponentData(Struct):
    def __init__(self, **kwargs):
        super(GcScannableComponentData, self).__init__()

        """ Contents of the struct """

        self.data['ScanRange'] = kwargs.get('ScanRange', 300)
        self.data['ScanName'] = kwargs.get('ScanName', "")
        self.data['ScanTime'] = kwargs.get('ScanTime', 30)
        self.data['IconType'] = kwargs.get('IconType', GcScannerIconTypes())
        self.data['PermanentIcon'] = kwargs.get('PermanentIcon', False)
        self.data['PermanentIconRadius'] = kwargs.get('PermanentIconRadius', 0)
        """ End of the struct contents"""
