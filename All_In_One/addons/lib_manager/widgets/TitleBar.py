import sys

from PyQt5.QtWidgets import QDialog,QLabel,QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from ..functions import icon_path

class TitleBar(QDialog):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        css = """
        QWidget{
            Background: #AA00AA;
            color:white;
            font:12px bold;
            font-weight:bold;
            border-radius: 1px;
            height: 11px;
        }
        QDialog{
            font-size:12px;
            color: black;

        }
        QToolButton{
            Background:#AA00AA;
            font-size:11px;
        }
        QToolButton:hover{
            Background: #FF00FF;
            font-size:11px;
        }
        """
        #self.setAutoFillBackground(True)
        #self.setBackgroundRole(QtGui.QPalette.Highlight)
        self.setStyleSheet(css)
        self.minimize=QtWidgets.QToolButton(self)
        self.minimize.setIcon(QtGui.QIcon(icon_path("ICON_MINIMIZE")))
        self.maximize=QtWidgets.QToolButton(self)
        self.maximize.setIcon(QtGui.QIcon(icon_path("ICON_MAXIMIZE")))
        close=QtWidgets.QToolButton(self)
        close.setIcon(QtGui.QIcon(icon_path("ICON_CLOSE")))
        self.minimize.setMinimumHeight(10)
        close.setMinimumHeight(10)
        self.maximize.setMinimumHeight(10)
        label=QLabel(self)
        label.setText("Window Title")
        self.setWindowTitle("Window Title")
        hbox=QtWidgets.QHBoxLayout(self)
        hbox.addWidget(label)
        hbox.addWidget(self.minimize)
        hbox.addWidget(self.maximize)
        hbox.addWidget(close)
        hbox.insertStretch(1,500)
        hbox.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.maxNormal=False
        close.clicked.connect(self.close)
        self.minimize.clicked.connect(self.showSmall)
        self.maximize.clicked.connect(self.showMaxRestore)

    def showSmall(self):
        self.showMinimized()

    def showMaxRestore(self):
        if(self.maxNormal):
            self.showNormal()
            self.maxNormal= False
            self.maximize.setIcon(QIcon(icon_path("ICON_MAXIMIZE")))

        else:
            self.showMaximized()
            self.maxNormal=  True
            self.maximize.setIcon(QIcon(icon_path("ICON_MAXIMIZE_2")))

    def close(self):
        self.close()

    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()

    def mouseMoveEvent(self,event):
        if self.moving: self.move(event.globalPos()-self.offset)
