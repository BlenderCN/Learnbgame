from PyQt5.QtWidgets import QPushButton,QSizePolicy
from PyQt5.QtGui import QIcon
from ..functions import get_css

class PushButton(QPushButton) :
    def __init__(self,text=None,icon=None,size=None):
        super().__init__()
        self.text = text
        self.icon = icon
        self.setStyleSheet(get_css('PushButton'))
        self.size = size

        self.createWidget()

    def createWidget(self) :
        if self.text :
            self.setText(self.text)

        if self.size :
            addAssetSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            self.setMaximumSize(self.size[0],self.size[1])
            self.setSizePolicy(addAssetSizePolicy)

        if self.icon :
            self.setIcon(QIcon(self.icon))
