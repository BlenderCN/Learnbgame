from PyQt5.QtWidgets import QPushButton,QSizePolicy,QFileDialog
from PyQt5.QtGui import QIcon
from ..functions import get_css,icon_path

class BtnFolder(QPushButton) :
    def __init__(self,field):
        super().__init__()
        self.field = field
        self.icon = icon_path('ICON_FOLDER')
        self.setStyleSheet(get_css('PushButton'))
        self.size = [22,22]

        self.clicked.connect(self.set_folder)
        self.setToolTip('Set Folder')
        self.createWidget()

    def set_folder(self) :
        self.field.setText(str(QFileDialog.getExistingDirectory(self, "Select Directory")))


    def createWidget(self) :
        if self.size :
            addAssetSizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            self.setMaximumSize(self.size[0],self.size[1])
            self.setSizePolicy(addAssetSizePolicy)

        if self.icon :
            self.setIcon(QIcon(self.icon))
