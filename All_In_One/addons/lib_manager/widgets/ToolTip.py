from PyQt5.QtWidgets import QToolTip
from ..functions import get_css

class ToolTip(QToolTip) :
    def __init__(self):
        super().__init__()
        #self.text = text
        self.setStyleSheet(get_css('ToolTip'))
        #self.size = size

        self.createWidget()

    def createWidget(self) :
        pass
