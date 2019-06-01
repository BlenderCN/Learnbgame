import sys, logging, os
import bpy
import subprocess
from importlib import import_module
from math import trunc

from PyQt5.QtWidgets import QWidget,QFrame,QVBoxLayout,QHBoxLayout,QSplitter,QSplitter,QShortcut,QSizePolicy,QListWidgetItem,QPlainTextEdit,QLabel,QSpacerItem,QPlainTextEdit,QToolTip,QListView
from PyQt5.QtCore import QDir,Qt,QSize,QFileInfo,QModelIndex
from PyQt5.QtGui import QIcon,QKeySequence,QPixmap

from .functions import *
from .widgets import *

from os.path import join,dirname,normpath

working_dir = os.path.dirname(os.path.realpath(__file__))
settings = read_json(os.path.join(working_dir,"settings.json"))

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.asset_type = get_asset_type()
        self.settings = settings
        self.working_dir = working_dir

        self.title = None
        self.treeWidget = None
        self.cbox_filter = None
        self.widget_close = None
        #self.view_mode = None
        self.context = None
        self.thumbnailList = None

        #self.folders = folder

        QDir.setCurrent(working_dir)

        self.setWindowTitle('Lib Manager')
        self.resize(840, 480)

        self.color_background = '#404040'
        self.color_text_field = '#A7A7A7'
        self.color_button = '#979797'
        self.color_panel_bright = '#727272'
        self.color_panel_dark = '#525252'
        self.color_border = '#2E2E2E'

        self.setUI()

        #self.style_button = "border-color: %s;background-color:%s;"%(self.color_border,self.color_button)

    def setUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.mainLayout = QVBoxLayout()

        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.setStyleSheet(get_css("MainWindow"))

        #Title Bar
        self.area = ComboBox()
        self.area.setStyleSheet(get_css("ComboBoxArea"))
        self.area.currentIndexChanged.connect(self.change_area)

        #self.area.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.area.setFixedWidth(32)

        #self.area.setMinimumWidth(32)
        #self.area.setMinimumHeight(28)

        #Populate the step_filter by the steps in settings

        self.area.addItem(QIcon(icon_path("ICON_GROUP")), "Library")
        self.area.addItem(QIcon(icon_path("ICON_MATERIAL")), "Assets")
        self.area.addItem(QIcon(icon_path("ICON_ARMATURE_DATA")), "Picker")
        self.area.addItem(QIcon(icon_path("ICON_SETTINGS")), "Prefs")

        self.titleBarArea = QFrame()
        self.titleBarLayout = QHBoxLayout()
        self.titleBarArea.setLayout(self.titleBarLayout)
        self.titleBarLayout.setContentsMargins(4, 0, 0, 0)
        self.titleBarArea.setStyleSheet("""
                            border : none; background-color : rgb(100,100,100);
                            border-style: solid;
                            border-color: rgb(50, 50, 50);
                            border-bottom-width: 1px;""")

        self.titleBarArea.setMinimumHeight(28)
        self.titleBarArea.setMaximumHeight(28)

        self.title = Label(text = 'Library')

        #self.toolBox = QFrame()

        self.toolBoxLayout = QHBoxLayout()
        self.toolBoxLayout.setContentsMargins(12, 0, 12, 0)

        # Batch
        self.btn_batch = PushButton(icon = icon_path("ICON_CONSOLE"),size = [22,22])
        self.btn_batch.clicked.connect(self.batch)
        self.btn_batch.setToolTip('Batch')

        # Add asset
        self.btn_add_asset = PushButton(icon = icon_path("ICON_ZOOMIN"),size = [22,22])
        self.btn_add_asset.clicked.connect(self.add_asset)
        self.btn_add_asset.setToolTip('Add an asset')

        # Settings Button
        self.btn_settings = PushButton(icon = icon_path("ICON_SETTINGS"),size = [22,22])
        self.btn_settings.setToolTip('Settings')

        # Add button to layout
        self.toolBoxLayout.addWidget(self.btn_batch)
        self.toolBoxLayout.addWidget(self.btn_add_asset)
        self.toolBoxLayout.addWidget(self.btn_settings)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hSpacer = QSpacerItem(30, 20, QSizePolicy.Maximum, QSizePolicy.Minimum)

        self.titleBarLayout.addWidget(self.area)
        self.titleBarLayout.addWidget(self.title)
        self.titleBarLayout.addItem(self.horizontalSpacer)
        self.titleBarLayout.addLayout(self.toolBoxLayout)
        #self.titleBarLayout.addItem(self.hSpacer)

        #top Bar
        self.topBarArea = QFrame()
        self.topBarArea.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.topBarArea.setMinimumHeight(32)
        self.topBarArea.setMaximumHeight(32)

        self.topBarLayout = QHBoxLayout()
        self.topBarLayout.setSpacing(2)
        self.topBarLayout.setContentsMargins(4, 1, 4, 1)

        self.topBarArea.setLayout(self.topBarLayout)
        self.topBarArea.setStyleSheet(get_css('Bar'))

        #Left Panel
        self.leftPanel = QFrame()
        #self.leftPanel.setMaximumWidth(132)


        self.leftPanel.setStyleSheet(get_css('PanelLeft'))

        self.leftPanelLayout = QVBoxLayout()
        self.leftPanelLayout.setContentsMargins(0, 0, 0, 0)
        self.leftPanel.setLayout(self.leftPanelLayout)

        self.outlinerLayout = QVBoxLayout()
        self.outlinerLayout.setContentsMargins(1, 5, 1, 1)

        self.outlinerTopBarLayout = QVBoxLayout()
        self.outlinerTopBarLayout.setContentsMargins(0, 0, 0, 0)

        self.treeWidget = TreeWidget()
        self.treeWidget.create_widget(settings['path'])
        self.treeWidget.itemClicked.connect(self.click_item)


        # comboBox asset cbox_asset_choice
        self.cbox_filter = ComboBox()
        self.cbox_filter.currentIndexChanged.connect(self.change_filter)
        self.cbox_filter.setFixedHeight(28)

        self.cbox_filter.setStyleSheet(get_css("ComboBoxAsset"))

        #self.cbox_asset_choice.setStyleSheet("border-left : none; border-right : none; border-top : none")
        self.cbox_filter.addItem(QIcon(icon_path("ICON_ACTION")), "All")

        for item,info in sorted(self.asset_type.items()):
            self.cbox_filter.addItem(QIcon(info['icon']), item.title(),info['image'])
            #filter_item.image_path =

        self.outlinerTopBarLayout.addWidget(self.cbox_filter)
        self.outlinerLayout.addWidget(self.treeWidget)

        self.leftPanelLayout.addLayout(self.outlinerTopBarLayout)
        self.leftPanelLayout.addLayout(self.outlinerLayout)

        #Tool Box
        self.toolBoxPanel = QFrame()
        self.toolBoxPanel.setStyleSheet("border : none; background-color : rgb(100,100,100)")
        self.toolBoxLayout  = QVBoxLayout()

        self.toolBoxPanel.setLayout(self.toolBoxLayout)

        self.leftPanelLayout.addWidget(self.toolBoxPanel)

        #Middle
        self.middle = QFrame()
        self.middle.setStyleSheet(get_css('2DSpace'))

        self.middleLayout = QVBoxLayout()
        self.middleLayout.setContentsMargins(0, 0, 0, 0)
        self.middleLayout.setSpacing(0)

        self.thumbnailList = ListWidget(self)
        self.assetLayout = QVBoxLayout()
        self.assetLayout.setContentsMargins(0, 0, 0, 0)

        self.assetLayout.addWidget(self.thumbnailList)

        #vSpacer = QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.assetLayout.addItem(vSpacer)

        #self.change_view_mode()
        #self.thumbnailList.itemClicked.connect(self.click_thumb)
        #self.thumbnailList = TableWidget(self)


        self.middleLayout.addWidget(self.topBarArea)
        self.middleLayout.addLayout(self.assetLayout)

        self.middle.setLayout(self.middleLayout)


        #Right Panel
        self.rightPanel = QFrame()
        #self.rightPanel.setMaximumWidth(256)
        #self.rightPanel.setMinimumWidth(256)


        self.rightPanel.setStyleSheet(get_css('PanelRight'))

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setContentsMargins(0, 0, 0, 0)
        self.rightLayout.setSpacing(0)

        self.rightPanel.setLayout(self.rightLayout)


        #Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(get_css('Splitter'))
        #self.splitter.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        ## Dir button
        btn_parent_dir = PushButton(icon= icon_path('ICON_FILE_PARENT'),size = [22,22])

        #### add_asset button
        #btn_add_asset = PushButton(icon= icon_path('ICON_ZOOMIN'),size = [22,22])
        #btn_add_asset.clicked.connect(self.add_asset)

        btn_refresh = PushButton(icon= icon_path('ICON_FILE_FOLDER'),size = [22,22])
        btn_refresh.clicked.connect(self.refresh)
        btn_refresh.setToolTip('Refresh tree')

        #open folder button
        btn_open_folder= PushButton(icon = icon_path('OPEN_FOLDER'),size = [22,22])
        btn_open_folder.clicked.connect(self.open_folder)
        btn_open_folder.setToolTip('Open Lib Folder')

        #list view
        spacer = QSpacerItem(5, 5, QSizePolicy.Maximum, QSizePolicy.Minimum)
        self.view_mode = CheckBox('List')
        self.view_mode.stateChanged.connect(lambda : self.click_item(self.treeWidget.currentItem()))

        #search bar
        self.search_bar = LineEdit()
        self.search_bar.textChanged.connect(self.filterThumbnail)

        #add widget to search bar
        self.topBarLayout.addWidget(btn_parent_dir)
        self.topBarLayout.addWidget(self.search_bar)
        self.topBarLayout.addWidget(btn_refresh)
        self.topBarLayout.addWidget(btn_open_folder)
        self.topBarLayout.addItem(spacer)
        self.topBarLayout.addWidget(self.view_mode)


        # Adding Panel to splitter
        self.splitter.addWidget(self.leftPanel)
        self.splitter.addWidget(self.middle)
        self.splitter.addWidget(self.rightPanel)

        self.splitter.setSizes([132,512,256])

        self.splitter.setStretchFactor(0,0)
        self.splitter.setStretchFactor(1,1)
        self.splitter.setStretchFactor(2,0)

        self.mainLayout.addWidget(self.titleBarArea)
        self.mainLayout.addWidget(self.splitter)

        #shortcut
        self.shortcut_zoom_in = QShortcut(QKeySequence("+"), self)
        self.shortcut_zoom_out = QShortcut(QKeySequence("-"), self)

        self.shortcut_zoom_in.activated.connect(self.zoom_in)
        self.shortcut_zoom_out.activated.connect(self.zoom_out)


        self.setLayout(self.mainLayout)
        self.show()

    def change_view_mode(self) :
        self.click_item(self.treeWidget.currentItem)

    def batch(self) :
        clear_layout(self.rightLayout)

        #self.addAssetPanel = Batch(self)

        self.rightLayout.addLayout(Batch(self))
        #def batch_fill_lib(template,files,folder = None,category = None) :
        #self.click_item(self.treeWidget.currentItem)


    def change_filter(self,index) :
        print( str(self.cbox_filter.currentText()))


    def change_area(self,index) :
        #self.treeWidget.clear()
        print( str(self.area.currentText()))
        if self.title :
            self.title.setText(self.area.currentText())

        #self.refresh()


    def refresh(self) :
        area = str(self.area.currentText())

        if self.treeWidget and self.area and self.cbox_filter:
            if self.treeWidget.search_json.isRunning :
                self.treeWidget.search_json.terminate()
            self.treeWidget.clear()

        #filter_items = str(self.cbox_filter.currentText())

        self.treeWidget.create_widget(settings['path'])
        #self.treeWidget.create_tree(settings['path'],'Library','All')


    def open_folder(self) :
        try:
            os.startfile(settings['path'])
        except:
            subprocess.Popen(['xdg-open', settings['path']])

    def add_asset(self) :
        clear_layout(self.rightLayout)

        self.addAssetPanel = AddAsset(self)

        self.rightLayout.addLayout(self.addAssetPanel)


    def zoom_in(self) :
        new_size = self.thumbnailList.iconSize().width()
        if not new_size >512 :
            new_size*=1.25

        self.thumbnailList.setIconSize(QSize(new_size,new_size))
        #self.thumbnailList.setStyleSheet("QListView::item {height: %s;}"%(new_size+6))

    def zoom_out(self) :
        new_size = self.thumbnailList.iconSize().width()
        if not new_size <16 :
            new_size*=0.75

        self.thumbnailList.setIconSize(QSize(new_size,new_size))
        #self.thumbnailList.setStyleSheet("QListView::item {height: %s;}"%(new_size+6))

    # When selected of folder in the outliner
    def click_item(self,item):
        #for row in range(self.thumbnailList.rowCount()) :
        #clear_layout(self.assetLayout)
        #self.thumbnailList.clear()
        #a= TreeWidget(item.text(1))
        #self.thumbnailList.clear()
        #self.middle.addWidget(ThumbnailPanel.createWidget(item.text(1)))
        if hasattr(self,'view_mode') and self.view_mode.isChecked() :
            self.thumbnailList = TableWidget(self)
            #self.thumbnailList.horizontalHeader().setSortIndicator(1,Qt.AscendingOrder)
            #self.thumbnailList.cellClicked.connect(self.click_thumb)
            #self.thumbnailList.setRowCount(0)
        else :
            if hasattr(self.thumbnailList,"search_asset") and self.thumbnailList.search_asset.isRunning :
                self.thumbnailList.search_asset.terminate()
                self.thumbnailList.clear()

            self.thumbnailList.search_images(item.full_path)
            #self.thumbnailList.itemClicked.connect(self.click_thumb)
            #self.thumbnailList.clear()


        #print(item.full_path)



        #self.asset_list.sort(key = lambda x : x[''])

        #self.assetLayout.addWidget(self.thumbnailList)

        if self.area.currentText()== 'Library' :
            subFolder = []

    # When taping in the search bar
    def filterThumbnail(self) :
        if self.thumbnailList :
            items = (self.thumbnailList.item(i) for i in range(self.thumbnailList.count()))
            search = self.search_bar.text()

            for index,item in enumerate(items) :
                info = item.info
                tags = [t for t in info['tags'].split(',') if len(info['tags'])]
                name = info['asset']

                item_visibility = filtering_keyword(name,search,tags)

                if self.view_mode.isChecked() :
                    self.thumbnailList.setRowHidden(index,item_visibility)
                else :
                    self.thumbnailList.item(index).setHidden(item_visibility)


    def closeEvent(self, event):
        if self.treeWidget.search_json.isRunning :
            self.treeWidget.search_json.terminate()


        if hasattr(self.thumbnailList,"search_asset") and self.thumbnailList.search_asset.isRunning :
            self.thumbnailList.search_asset.terminate()

        self.widget_close = True
        self.deleteLater()


        #self.setGeometry(300, 300, 300, 200)
