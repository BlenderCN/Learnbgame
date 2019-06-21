from PyQt5.QtWidgets import QLabel,QSizePolicy,QFrame,QVBoxLayout
from PyQt5.QtGui import QPixmap,QPainter
from PyQt5.QtCore import QSize,Qt,QPoint
from ..functions import get_css

class Image(QFrame) :
    def __init__(self,text = None,img = None):
        super().__init__()
        self.text = text
        self.img = img

        self.setStyleSheet(get_css('Image'))

        print(self.img)
        self.createWidget()

    def createWidget(self) :
        #self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.pic = QPixmap(self.img)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(4,4,4,4)

        self.thumb = QLabel()

        self.thumb.setStyleSheet("border-image: url(%s) 0 0 0 0 stretch stretch;"%self.img)

        self.layout.addWidget(self.thumb)
        self.setLayout(self.layout)

        #ratio = self.pic.width()/self.pic.height()

        #print(ratio)
        #self.setFixedHeight(self.thumb.width()*ratio)
        #self.resize(self.width(),self.width()*ratio)

    def resizeEvent(self, event):
        ratio = self.pic.width()/self.pic.height()
        #self.setPixmap(self.thumb.scaled(event.size().width(),event.size().width(),Qt.KeepAspectRatio))
        #self.move(0,0)

        self.setFixedHeight(event.size().width()*ratio)
        #self.resize(event.size().width(),event.size().width()*ratio)
