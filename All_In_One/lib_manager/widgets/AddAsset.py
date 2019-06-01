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


from ..functions import get_css,icon_path,clear_layout,read_json,image_path

import bpy,os,importlib


class AddAsset(QVBoxLayout) :
    def __init__(self, parent=None):
        super().__init__(parent)

        self.previewImage = None
        self.parent = parent
        self.screenshot = None
        self.createWidget()

    def createWidget(self) :
        #self.mainLayout = QVBoxLayout()
        self.setContentsMargins(12, 6, 6, 6)
        self.setSpacing(8)

        self.mainLayout = QVBoxLayout()

        #asset Type Choice
        self.assetType = ComboBox()
        self.assetType.currentIndexChanged.connect(self.set_layout)
        self.assetType.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.assetType.setStyleSheet(get_css("ComboBoxAsset"))
        for item,info in sorted(self.parent.asset_type.items()):
            self.assetType.addItem(QIcon(info['icon']), item.title().replace('_',' '))

        self.assetTypeLayout = QHBoxLayout()
        self.assetTypeLayout.addWidget(Label(text = 'Type :'))
        self.assetTypeLayout.addWidget(self.assetType)

        self.addLayout(self.assetTypeLayout)


        self.addLayout(self.mainLayout)


    def set_layout(self):
        from .. import asset_managing as asset_managing
        assetType = self.assetType.currentText().lower().replace(' ','_')

        store_func = self.parent.asset_type[assetType]['store']+'_settings'

        module = getattr(asset_managing,assetType)



        clear_layout(self.mainLayout)

        print(self.assetType.currentText())


        self.previewImagePanel = QFrame()
        self.previewImageLayout = QVBoxLayout()
        self.previewImagePanel.setLayout(self.previewImageLayout)
        self.previewImagePanel.setMinimumSize(230,230)
        self.previewImagePanel.setMaximumSize(230,230)
        #­self.previewImage.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.previewImagePanel.setStyleSheet("border-style : dashed;border-width : 2px; border-color:rgb(60,60,60);background-color : rgb(100,100,100);")
        self.previewImageLayout.setContentsMargins(0, 0, 0, 0)
        #self.previewImageLayout.setSpacing(0)

        # Asset Name
        self.assetName = LineEdit()
        self.assetNameRow = QHBoxLayout()
        self.assetNameRow.addWidget(Label(text = 'Name :'))
        self.assetNameRow.addWidget(self.assetName)

        # Category Completion
        #self.model = QStringListModel()
        #self.model.setStringList(['pose','mains','expressions','cycle'])
        #self.cat_completer = QCompleter()
        #self.cat_completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        #self.cat_completer.setModel(self.model)

        # Category Name
        self.assetCategory = LineEdit()
        self.assetCategoryRow = QHBoxLayout()
        self.assetCategoryRow.addWidget(Label(text='Category :'))
        self.assetCategoryRow.addWidget(self.assetCategory)

        # tag List
        self.assetTags = LineEdit()
        self.assetTagsRow = QHBoxLayout()
        self.assetTagsRow.addWidget(Label(text='Tags :'))
        self.assetTagsRow.addWidget(self.assetTags)

        # Description
        self.assetDescription = QPlainTextEdit()
        self.assetDescription.setStyleSheet(get_css('LineEdit'))
        self.assetDescriptionRow = QHBoxLayout()
        self.assetDescriptionRow.addWidget(Label(text='Description :'))
        self.assetDescriptionRow.addWidget(self.assetDescription)

        # Adding layout to main Widget
        self.mainLayout.addWidget(self.previewImagePanel)
        self.mainLayout.addLayout(self.assetNameRow)
        self.mainLayout.addLayout(self.assetCategoryRow)
        self.mainLayout.addLayout(self.assetTagsRow)
        self.mainLayout.addLayout(self.assetDescriptionRow)

        #add settings per Asset type
        #getattr(asset_storing, store_func)(self)
        getattr(module,store_func)(self)

        # tools layout
        self.toolsLayout = QHBoxLayout()
        horizontalSpacer = QSpacerItem(128, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        verticalSpacer = QSpacerItem(20, 16, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.toolsLayout.addItem(horizontalSpacer)
        #thumbnail button
        self.btn_thumbnail = PushButton(icon = icon_path('ICON_RENDER_REGION'),size = [24,24])
        self.btn_thumbnail.clicked.connect(self.set_thumbnail)
        #ok_button
        self.btn_ok = PushButton(text = 'OK')
        self.btn_ok.clicked.connect(self.ok)
        #cancel_button
        self.btn_cancel = PushButton(text = 'Cancel')
        self.btn_cancel.clicked.connect(self.cancel)

        self.toolsLayout.addWidget(self.btn_thumbnail)
        self.toolsLayout.addWidget(self.btn_ok)
        #self.toolsLayout.addWidget(self.btn_cancel)


        self.mainLayout.addItem(verticalSpacer)
        self.mainLayout.addLayout(self.toolsLayout)

    def update_number(self) :
        img_frame = round((int(self.frameRangeOut.text()) - int(self.frameRangeIn.text())) / int(self.step.text()))

        self.imgNumber.setText(str(img_frame))

    def ok(self):
        from .. import asset_managing as asset_managing
        assetType = self.assetType.currentText().lower().replace(' ','_')

        store_func = self.parent.asset_type[assetType]['store']

        module = getattr(asset_managing,assetType)
        getattr(module,store_func)(self)

        #store_func = settings['item_type'][assetType]['store']
        #getattr(asset_storing, store_func)(self)

        #store_func(self)
    def cancel(self):
        bar = TitleBar(parent = self.parent)
        TitleBar.show()
        ('print cancel')

    def show_completion(self) :
        self.setPopup(QAbstractItemView())


    def set_thumbnail(self) :
        active_ob = bpy.context.scene.objects.active
        clear_layout(self.previewImageLayout)

        '''
        #for all 3d view show only render set to true
        view_settings={}
        view_settings['VIEW_3D'] = {}
        view_settings['bg_color'] = bpy.context.user_preferences.themes['Default'].view_3d.space.gradients.high_gradient
        bpy.context.user_preferences.themes['Default'].view_3d.space.gradients.high_gradient = (0.5,0.5,0.5)

        for index,area in enumerate(bpy.context.window_manager.windows[0].screen.areas) :
            if area.type == 'VIEW_3D' :
                only_render = area.spaces[0].show_only_render
                world = area.spaces[0].show_world

                view_settings['VIEW_3D'][index] = [only_render,world]
                area.spaces[0].show_only_render = True
                area.spaces[0].show_world = True
        '''

        main = Rubb(parent = self.parent)
        main.fullScreenLabel.show()

        if active_ob and active_ob.type == 'ARMATURE' :
            if active_ob.proxy_group :
                self.asset = active_ob.proxy_group.name

            else :
                self.asset = active_ob.name
