from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize,Qt
from ..functions import get_css

class Label(QLabel) :
    def __init__(self,text = None):
        super().__init__()
        self.text = text

        self.setStyleSheet(get_css('Label'))

        self.createWidget()

    def createWidget(self) :
        self.setText(self.text)
