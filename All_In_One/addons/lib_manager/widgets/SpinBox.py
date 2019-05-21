from PyQt5.QtWidgets import QSpinBox
from ..functions import get_css

class SpinBox(QSpinBox) :
    def __init__(self):
        super().__init__()
        #self.text = text
        self.setStyleSheet(get_css('SpinBox'))
        #self.size = size

        self.createWidget()

    def createWidget(self) :
        pass
