from PyQt5.QtWidgets import QVBoxLayout,QHBoxLayout,QCompleter,QSpinBox,QSpacerItem,QCheckBox,QSizePolicy,QLabel,QFrame,QApplication,QPlainTextEdit
from PyQt5.QtCore import QStringListModel,Qt
from PyQt5.QtGui import QPixmap,QIcon

from .ComboBox import ComboBox
from .PushButton import PushButton
from .LineEdit import LineEdit
from .Label import Label
from .SpinBox import SpinBox
from .CheckBox import CheckBox
from .Rubb import Rubb
from .TitleBar import TitleBar
from .Image import Image

from ..functions import get_css,icon_path,clear_layout,read_json,image_path

import bpy,os,importlib,json


class AssetInfo(QVBoxLayout) :
    def __init__(self, parent=None,info=None):
        super().__init__(parent)

        self.info = info
        self.parent = parent

        if self.info :
            self.createWidget()

    def text_edited(self,info,key,text):
        info[key] = text

        with open(info['info_path'], 'r') as f:
            data = json.load(f)
            data[key] = text

        with open(info['info_path'], 'w') as outfile:
            json.dump(data, outfile)

    def createWidget(self) :
        item_info = self.info

        img = QPixmap(item_info['image'])
        ratio = img.width()/img.height()

        #Preview Image
        self.previewImage = Image(img = item_info['image'])
        self.previewImage.setFixedHeight(self.parent.rightPanel.width()*ratio)

        #set text
        self.textLayout = QVBoxLayout()
        self.textLayout.setContentsMargins(8, 8, 8, 8)
        self.textLayout.setSpacing(5)

        #self.textPanel.setLayout(self.textLayout)
        #Fill layout
        #Text description

        # Asset Name
        self.assetName = LineEdit(text=os.path.splitext(item_info['asset'])[0])

        self.assetNameLayout = QHBoxLayout()
        self.assetNameLayout.addWidget(Label(text = 'Name :'))
        self.assetNameLayout.addWidget(self.assetName)

        # asset tag
        self.assetTag = LineEdit(text=item_info['tags'])
        self.assetTag.textChanged.connect(lambda : self.text_edited(item_info,'tags',self.assetTag.text()))
        self.assetTagLayout = QHBoxLayout()
        self.assetTagLayout.addWidget(Label(text = 'Tags :'))
        self.assetTagLayout.addWidget(self.assetTag)

        # asset type
        self.assetType = LineEdit(text=item_info['type'])
        self.assetTypeLayout = QHBoxLayout()
        self.assetTypeLayout.addWidget(Label(text = 'Type :'))
        self.assetTypeLayout.addWidget(self.assetType)

        # Description
        self.assetDescription = QPlainTextEdit()
        self.assetDescription.textChanged.connect(lambda : self.text_edited(item_info,'description',self.assetDescription.toPlainText()))
        self.assetDescription.setPlainText(item_info['description'])
        self.assetDescription.setStyleSheet(get_css('LineEdit'))
        #self.assetDescription.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.assetDescriptionLayout = QVBoxLayout()
        self.assetDescriptionLayout.addWidget(Label(text = 'Description :'))
        self.assetDescriptionLayout.addWidget(self.assetDescription)

        vSpacer1 = QSpacerItem(20, 10, QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Fill Text Layout
        self.textLayout.addLayout(self.assetNameLayout)
        self.textLayout.addLayout(self.assetTagLayout)
        self.textLayout.addLayout(self.assetTypeLayout)
        self.textLayout.addItem(vSpacer1)
        self.textLayout.addLayout(self.assetDescriptionLayout)



        vSpacer2 = QSpacerItem(20, 80, QSizePolicy.Expanding, QSizePolicy.Expanding)


        self.addWidget(self.previewImage)
        self.addLayout(self.textLayout)
        self.addItem(vSpacer2)
