from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem,QHeaderView,QAbstractItemView,QMenu,QAction
from PyQt5.QtCore import QSize,QPoint,Qt
from PyQt5.QtGui import QIcon,QPixmap

from . AssetInfo import AssetInfo

from ..functions import get_css,icon_path,read_json,image_path,clear_layout

import bpy,os

working_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
settings = read_json(os.path.join(working_dir,"settings.json"))

#from .. import settings

class TableWidget(QTableWidget):
    def __init__(self,parent):
        super().__init__(parent)

        self.attributes = ['icon','asset','tags','type','description','info_path','path','image']
        #self.folder = settings.paths
        self.parent = parent
        self.setColumnCount(len(self.attributes))
        #self.setRowCount(5)
        #self.setColumnWidth(0,32)
        self.setStyleSheet(get_css('TableWidget'))
        self.setIconSize(QSize(48,48))

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.horizontalHeader().setSectionResizeMode(1)
        self.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)

        #Interactive

        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(38)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)
        self.setSortingEnabled(True)

        #self.cellClicked.connect(self.cell_clicked)
        self.cellClicked.connect(self.click_thumb)
        self.setHorizontalHeaderLabels(self.attributes)

    def set_row(self,item_info,row_index) :
        self.insertRow(row_index)

        for attr in self.attributes :
            value = item_info[attr]

            item = QTableWidgetItem()
            #item.info = item_info

            if attr == 'icon' :
                item.setIcon(QIcon(value))
            else :
                item.setText(value)

            self.setItem(row_index, self.attributes.index(attr), item)

            print(row_index)

        row_index+=1


    # display information when clicking on a thumbnail
    def click_thumb(self,item) :
        clear_layout(self.parent.rightLayout)

        item_info = {}
        for j in range(self.columnCount()):
            item_info[self.horizontalHeaderItem(j).text()] = self.item(item,j).text()


        self.AssetInfo = AssetInfo(self.parent,item_info)

        self.parent.rightLayout.addLayout(self.AssetInfo)


    def on_context_menu(self, QPos):
        self.listMenu= QMenu()
        link = QAction(QIcon(icon_path('ICON_LINK_BLEND')), 'Link', self)
        link.triggered.connect(lambda : self.menu_item_link(link=True))

        append = QAction(QIcon(icon_path('ICON_APPEND_BLEND')), 'Append', self)
        append.triggered.connect(lambda : self.menu_item_link(link=False))

        delete = QAction(QIcon(icon_path('ICON_CLOSE')), 'Delete', self)
        delete.triggered.connect(self.menu_item_delete)

        self.listMenu.addAction(link)
        self.listMenu.addAction(append)
        self.listMenu.addAction(delete)
        #menu_item.connect(self.menuItemClicked)
        parentPosition = self.mapToGlobal(QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def menu_item_link(self,link = True) :


        asset_type = self.parent.asset_type
        selected_rows = [i.row() for i in self.selectionModel().selectedRows()]

        headercount = self.columnCount()
        assets_info = []
        for i in selected_rows :
            asset_info = {}
            for j in range(headercount):
                asset_info[self.horizontalHeaderItem(j).text()] = self.item(i,j).text()

            assets_info.append(asset_info)

        self.offset = 0
        #self.scene = bpy.context.scene
        for asset_info in assets_info :
            from .. import asset_managing as asset_managing
            load_func = asset_type[asset_info['type']]['load']

            module = getattr(asset_managing,asset_info['type'])
            getattr(module,load_func)(self.parent,self,asset_info,link=link)

            self.offset +=1

        bpy.ops.ed.undo_push()


    def menu_item_delete(self) :
        #self.parent.treeWidget.clear()
        asset_list = self.parent.asset_list
        selected_rows = [i.row() for i in self.selectionModel().selectedRows()]
        import shutil
        paths = [asset_list[i].info['info_path'] for i in selected_rows]
        #self.parent.thumbnailList.clear()
        #self.parent.treeWidget.setCurrentItem(self.parent.treeWidget.headerItem())
        for path in paths:
            #self.takeItem(self.row(item))
            shutil.rmtree(os.path.dirname(path),ignore_errors=True)
