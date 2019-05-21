from PyQt5.QtWidgets import QComboBox
from ..functions import get_css

class ComboBox(QComboBox) :
    def __init__(self):
        super().__init__()

        self.setStyleSheet(get_css('ComboBox'))
        self.createWidget()

    def createWidget(self) :
        pass
