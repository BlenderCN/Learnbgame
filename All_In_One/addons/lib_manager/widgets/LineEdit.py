from PyQt5.QtWidgets import QLineEdit
from ..functions import get_css

class LineEdit(QLineEdit) :
    def __init__(self,text = None):
        super().__init__()
        self.setStyleSheet(get_css('LineEdit'))
        self.text_content = text
        self.createWidget()

    def createWidget(self) :
        if self.text :
            self.setText(self.text_content)
