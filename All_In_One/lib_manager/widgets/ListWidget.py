from PyQt5.QtWidgets import QListWidget,QListView,QAbstractItemView,QMenu,QAction,QListWidgetItem
from PyQt5.QtCore import QSize,QPoint,Qt,QDir,QThread,pyqtSignal
from PyQt5.QtGui import QIcon

from ..functions import get_css,icon_path,read_json,clear_layout,read_asset,filtering_keyword
from . AssetInfo import AssetInfo

import bpy,os

working_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
settings = read_json(os.path.join(working_dir,"settings.json"))

#from .. import settings


class SearchAsset(QThread) :
    item_found = pyqtSignal(dict)
    def __init__(self,parent=None,path = None):
        super(SearchAsset,self).__init__(parent)
        self.path = path
        self.parent = parent

    def run(self) :
        thumbnailList = self.parent

        for root, dirs, files in os.walk(self.path) :
            for f in sorted(files) :
                item_name,item_extension = os.path.splitext(f)
                item_path = os.path.join(root,f)

                if item_extension == '.json' :
                    item_info = read_asset(item_path)

                    '''
                    if item_info.get('image') and os.path.exists(item_info['image']):
                        image = item_info['image']
                    else :  #Use default icon
                        image = self.parent.parent.asset_type[item_info['type']]['image']
                        '''
                    #tags = [t for t in item_info['tags'].split(',') if len(t)]
                    #search = self.parent.parent.search_bar.text()

                    self.item_found.emit(item_info)
                    #item_visibility = filtering_keyword(item_info["asset"],search,tags)
                    #print(item_visibility)
                    #item = thumbnailList.set_item(item_info,item_visibility)
                    #item.setHidden(True)
                    #self.parent.parent.filterThumbnail()



class ListWidget(QListWidget):
    def __init__(self,parent):
        super().__init__(parent)

        #self.folder = settings.paths
        self.parent = parent
        #self.setStyleSheet(get_css('ThumbnailList'))
        #self.setViewMode(QListView.IconMode)
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setStyleSheet(get_css('ThumbnailList'))
        self.setAlternatingRowColors(True)
        self.setWrapping(True)
        self.setIconSize(QSize(128, 128))
        self.setMovement(QListView.Static)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)

        self.setSortingEnabled(True)

        self.itemDoubleClicked.connect(lambda : self.menu_item_link(True))
        self.itemClicked.connect(self.click_thumb)

    def search_images(self,path):
        self.search_asset = SearchAsset(self,path)
        self.search_asset.item_found.connect(self.set_item)
        self.search_asset.start()

    def set_item(self,item_info) :
        image = item_info["image"]
        if not item_info.get('image') or not os.path.exists(item_info['image']):
            image = self.parent.asset_type[item_info['type']]['image']

        item =QListWidgetItem(item_info['asset'])
        item.setIcon(QIcon(image))
        item.info = item_info

        image = item_info['image']

        tags = [t for t in item_info['tags'].split(',') if len(t)]
        search = self.parent.search_bar.text()
        item_visibility = filtering_keyword(item_info["asset"],search,tags)

        self.addItem(item)
        item.setHidden(item_visibility)

        return(item)

    def on_context_menu(self, QPos):
        self.listMenu= QMenu()
        link = QAction(QIcon(icon_path('ICON_LINK_BLEND')), 'Link', self)
        link.triggered.connect(lambda : self.menu_item_link(True))

        append = QAction(QIcon(icon_path('ICON_APPEND_BLEND')), 'Append', self)
        append.triggered.connect(lambda : self.menu_item_link(False))

        delete = QAction(QIcon(icon_path('ICON_CLOSE')), 'Delete', self)
        delete.triggered.connect(self.menu_item_delete)

        self.listMenu.addAction(link)
        self.listMenu.addAction(append)
        self.listMenu.addAction(delete)
        #menu_item.connect(self.menuItemClicked)
        parentPosition = self.mapToGlobal(QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()


    # display information when clicking on a thumbnail
    def click_thumb(self,item) :
        clear_layout(self.parent.rightLayout)

        item_info = item.info

        self.AssetInfo = AssetInfo(self.parent,item_info)

        self.parent.rightLayout.addLayout(self.AssetInfo)


    def menu_item_link(self,link=True) :


        asset_type = self.parent.asset_type
        selected_rows = [i.row() for i in self.selectionModel().selectedRows()]
        self.offset = 0
        print('####')
        #print([i['info'] for i in self.selectedItems()])
        #self.scene = bpy.context.scene
        for item in self.selectedItems() :
            from .. import asset_managing as asset_managing
            load_func = asset_type[item.info['type']]['load']

            module = getattr(asset_managing,item.info['type'])
            getattr(module,load_func)(self.parent,self,item.info,link=link)

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
