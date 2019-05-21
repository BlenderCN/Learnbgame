from PyQt5.QtWidgets import QCheckBox
from ..functions import get_css

class CheckBox(QCheckBox) :
    def __init__(self,text):
        super().__init__()
        self.text =text
        self.setStyleSheet(get_css('CheckBox'))
        self.createWidget()

    def createWidget(self) :
        self.setText(self.text)
