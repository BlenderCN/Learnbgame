
import sys
from PyQt5.QtGui import QIcon,QColor
from PyQt5.QtWidgets import QVBoxLayout,QHBoxLayout,QFrame,QSpacerItem,QWidget,QSizePolicy,QApplication,QGraphicsDropShadowEffect,QDialog
from PyQt5.QtCore import Qt,QDir

from . TitleBar import TitleBar
from . Label import Label
from . PushButton import PushButton
from . ComboBox import ComboBox

import os

from ..functions import icon_path,get_css

class WindowFrame(QDialog):
    def __init__(self):
        super(WindowFrame, self).__init__()
        self.closed = False
        self.maxNormal=False
        self.resize(840, 480)
        self.setMouseTracking(True)

        self.base_path = os.path.dirname(__file__)

        QDir.setCurrent(os.path.dirname(self.base_path))


        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.SplashScreen)
        #self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
        #self.setStyleSheet("border : none; background-color : rgba(250,100,100,0)")
        #self.setAutoFillBackground(True)
        #self.setAttribute(Qt.WA_TranslucentBackground)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        #Title Bar
        self.area = ComboBox()
        self.area.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.area.setMaximumWidth(32)
        #self.area.setMinimumWidth(32)
        #self.area.setMinimumHeight(28)

        self.area.addItem(QIcon(icon_path("ICON_ACTION")), "Prefs")
        self.area.addItem(QIcon(icon_path("ICON_GROUP")), "Library")
        self.area.addItem(QIcon(icon_path("ICON_MATERIAL")), "Assets")

        self.titleBarArea = QFrame()
        #self.titleBarArea.setCursor(Qt.OpenHandCursor)
        self.titleBarLayout = QHBoxLayout()
        self.titleBarLayout.setContentsMargins(4, 2, 4, 2)
        self.titleBarArea.setStyleSheet("""
                            border : none; background-color : rgb(100,100,100);
                            border-top-left-radius: 5px;border-top-right-radius: 5px;
                            border-style: solid;
                            border-color: rgb(50, 50, 50);
                            border-bottom-width: 1px;""")

        self.titleBarArea.setMinimumHeight(30)
        self.titleBarArea.setMaximumHeight(30)

        self.title = Label('Lib Manager')

        self.toolBox = QFrame()
        self.toolBox.setStyleSheet("""
                        border : none; background-color : rgb(120,120,120);
                        border-top-left-radius: 0px;border-top-right-radius: 0px;
                        border-bottom-left-radius: 5px;border-bottom-right-radius: 5px;""")
        self.toolBoxLayout = QHBoxLayout()
        self.toolBoxLayout.setContentsMargins(12, 0, 4, 0)
        self.toolBox.setLayout(self.toolBoxLayout)

        self.btn_add_asset = PushButton(icon = icon_path("ICON_ZOOMIN"),size = [22,22])
        self.btn_settings = PushButton(icon = icon_path("ICON_SETTINGS"),size = [22,22])

        self.toolBoxLayout.addWidget(self.btn_add_asset)
        self.toolBoxLayout.addWidget(self.btn_settings)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hSpacer = QSpacerItem(30, 20, QSizePolicy.Maximum, QSizePolicy.Minimum)

        self.btn_minimize= PushButton(icon = icon_path("ICON_MINIMIZE"),size = [22,22])
        self.btn_minimize.clicked.connect(self.showSmall)

        self.btn_maximize= PushButton(icon = icon_path("ICON_MAXIMIZE"),size = [22,22])
        self.btn_maximize.clicked.connect(self.showMaxRestore)

        self.btn_close = PushButton(icon = icon_path("ICON_CLOSE"),size = [22,22])
        self.btn_close.clicked.connect(self.close)

        self.titleBarLayout.addWidget(self.area)
        self.titleBarLayout.addWidget(self.title)
        self.titleBarLayout.addItem(self.horizontalSpacer)
        self.titleBarLayout.addWidget(self.toolBox)
        self.titleBarLayout.addItem(self.hSpacer)
        self.titleBarLayout.addWidget(self.btn_minimize)
        self.titleBarLayout.addWidget(self.btn_maximize)
        self.titleBarLayout.addWidget(self.btn_close)

        self.titleBarArea.setLayout(self.titleBarLayout)


        self.middleLayout = QHBoxLayout()

        self.handleList = [self.titleBarArea]
            #Left Bar
        self.leftBarLayout = QVBoxLayout()
        self.leftHandle = QFrame()
        self.leftHandle.setStyleSheet("border : none; background-color : rgb(110,110,110);")
        self.leftHandle.setMaximumWidth(5)
        self.leftHandle.setMinimumWidth(5)
        self.leftHandle.setCursor(Qt.SizeHorCursor)

        self.leftBottomHandle = QFrame()
        self.leftBottomHandle.setStyleSheet("border : none; background-color : rgb(110,110,110);")
        self.leftBottomHandle.setMaximumSize(5,16)
        self.leftBottomHandle.setCursor(Qt.SizeBDiagCursor)

        #Add handle to a list
        self.handleList+=[self.leftHandle,self.leftBottomHandle]

        self.leftBarLayout.addWidget(self.leftHandle)
        self.leftBarLayout.addWidget(self.leftBottomHandle)

            #Content
        #self.content = QFrame()
        self.contentLayout = QVBoxLayout()
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(0)
        #self.content.setLayout(self.contentLayout)


            #Right Bar
        self.rightBarLayout = QVBoxLayout()
        self.rightHandle = QFrame()
        self.rightHandle.setStyleSheet("border : none; background-color : rgb(110,110,110);")
        self.rightHandle.setMaximumWidth(5)
        self.rightHandle.setMinimumWidth(5)
        self.rightHandle.setCursor(Qt.SizeHorCursor)

        self.rightBottomHandle = QFrame()
        self.rightBottomHandle.setStyleSheet("border : none; background-color : rgb(110,110,110);")
        self.rightBottomHandle.setMaximumSize(5,16)
        self.rightBottomHandle.setCursor(Qt.SizeFDiagCursor)

        self.rightBarLayout.addWidget(self.rightHandle)
        self.rightBarLayout.addWidget(self.rightBottomHandle)

        #Add handle to a list
        self.handleList+=[self.rightHandle,self.rightBottomHandle]

        self.middleLayout.addLayout(self.leftBarLayout)
        self.middleLayout.addLayout(self.contentLayout)
        self.middleLayout.addLayout(self.rightBarLayout)

        self.bottomLayout = QHBoxLayout()

        self.bottomLeftHandle = QFrame()
        self.bottomLeftHandle.setStyleSheet("border : none; background-color : rgb(110,110,110);")
        self.bottomLeftHandle.setMaximumSize(16,5)
        self.bottomLeftHandle.setCursor(Qt.SizeBDiagCursor)

        self.bottomHandle = QFrame()
        self.bottomHandle.setStyleSheet("border : none; background-color : rgb(110,110,110);")
        self.bottomHandle.setMaximumHeight(5)
        self.bottomHandle.setMinimumHeight(5)
        self.bottomHandle.setCursor(Qt.SizeVerCursor)

        self.bottomRightHandle = QFrame()
        self.bottomRightHandle.setStyleSheet("border : none; background-color : rgb(110,110,110);")
        self.bottomRightHandle.setMaximumSize(16,5)
        self.bottomRightHandle.setCursor(Qt.SizeFDiagCursor)

        self.bottomLayout.addWidget(self.bottomLeftHandle)
        self.bottomLayout.addWidget(self.bottomHandle)
        self.bottomLayout.addWidget(self.bottomRightHandle)

        #Add handle to a list
        self.handleList+=[self.bottomHandle,self.bottomLeftHandle,self.bottomRightHandle]

        self.lowLayout = QVBoxLayout()
        self.lowLayout.addLayout(self.middleLayout)
        self.lowLayout.addLayout(self.bottomLayout)


        self.mainLayout.addWidget(self.titleBarArea)
        self.mainLayout.addLayout(self.lowLayout)


        ##Shadow
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setColor(QColor(50, 50, 50, 200))
        self.shadow.setXOffset(5)
        self.shadow.setYOffset(5)
        self.shadow.setBlurRadius(8)
        self.setGraphicsEffect(self.shadow)
        #self.shadow.setEnabled(False)


        self.setLayout(self.mainLayout)

    def setContent(self,content):
        self.contentLayout.addWidget(content)


    def showSmall(self):
        self.showMinimized()


    def showMaxRestore(self):
        if(self.maxNormal):
            self.showNormal()
            self.maxNormal= False
            self.btn_maximize.setIcon(QIcon(icon_path("ICON_MAXIMIZE")))

        else:
            self.showMaximized()
            self.maxNormal=  True
            self.btn_maximize.setIcon(QIcon(icon_path("ICON_MAXIMIZE_2")))

    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton and QApplication.widgetAt(event.globalPos()) in self.handleList:
            #print(QApplication.widgetAt(event.globalPos()))
            self.moving = True
            self.pos_x = event.pos().x()
            self.pos_y = event.pos().y()
            self.pos = event.pos()

    def mouseMoveEvent(self,event):

        x_offset = event.pos().x()-self.pos_x
        y_offset = event.pos().y()-self.pos_y

        if self.moving :
            if self.rightHandle.underMouse() :
                self.resize(self.frameGeometry().width()+x_offset,self.frameGeometry().height())
                self.pos_x += x_offset

            if self.leftHandle.underMouse() :
                self.move(event.globalPos().x()-self.pos_x,self.frameGeometry().y())
                self.resize(self.frameGeometry().width()-x_offset,self.frameGeometry().height())

            if self.bottomHandle.underMouse() :
                self.resize(self.frameGeometry().width(),self.frameGeometry().height()+y_offset)
                self.pos_y += y_offset

            if self.titleBarArea.underMouse() :
                self.move(event.globalPos()-self.pos)

            if self.rightBottomHandle.underMouse() or self.bottomRightHandle.underMouse():
                self.resize(self.frameGeometry().width()+x_offset,self.frameGeometry().height()+y_offset)
                self.pos_x += x_offset
                self.pos_y += y_offset

            if self.leftBottomHandle.underMouse() or self.bottomLeftHandle.underMouse():
                self.move(event.globalPos().x()-self.pos_x,self.frameGeometry().y())
                self.resize(self.frameGeometry().width()-x_offset,self.frameGeometry().height()+y_offset)
                #self.pos_x += x_offset
                self.pos_y += y_offset


    def close(self):
        self.closed = True
        self.deleteLater()
