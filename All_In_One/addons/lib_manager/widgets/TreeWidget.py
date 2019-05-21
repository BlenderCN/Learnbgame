from PyQt5.QtWidgets import QTreeWidget,QTreeWidgetItem,QTreeWidgetItemIterator
from PyQt5.QtCore import Qt,QThread,pyqtSignal
from PyQt5.QtGui import QFont,QIcon
from ..functions import get_css,icon_path, get_asset_from_xml,read_json,get_directory_structure

import os

working_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
settings = read_json(os.path.join(working_dir,"settings.json"))


class SearchJson(QThread) :
    scan_complete = pyqtSignal()
    def __init__(self,parent=None,path = None):
        super(SearchJson,self).__init__(parent)
        self.path = path
        self.parent = parent
        self.folders = {}

    def is_asset_folder(self,path) :
        path_name = os.path.basename(path)
        if [f for f in os.listdir(path) if os.path.splitext(f)[0]== path_name] :
            return True

    def recursive_dir(self,path,tree_root) :
        path_name = os.path.basename(path)
        #tree[path_name] ={}
        #tree_root = self.parent.tree_root

        for f in sorted(os.listdir(path)) :

            full_path = os.path.join(path,f)

            if os.path.isdir(full_path) and not self.is_asset_folder(full_path):
                temp_root = QTreeWidgetItem(tree_root, [f.title().replace('_',' '),f])
                temp_root.full_path = full_path
                self.recursive_dir(full_path,temp_root)

    def run(self) :
        self.folders = self.recursive_dir(self.path,self.parent.tree_root)
        self.scan_complete.emit()



class TreeWidget(QTreeWidget) :
    def __init__(self,filter=None):
        super().__init__()
        self.header().close()
        self.setStyleSheet(get_css('TreeWidget'))
        self.setAlternatingRowColors(True)
        self.setIndentation(15)
        self.tree_root = self.invisibleRootItem()
        #self.createWidget()


    def is_folder_in_path(self,path):
        for file in os.listdir(path) :
            full_path = os.path.join(path,file)
            if os.path.isdir(full_path) :
                return True
        return False


    def create_widget(self,path):
        #self.setStyleSheet(self.style_tree_view)
        #self.setStyleSheet("border: 10px solid #d9d9d9;")
        self.search_json = SearchJson(self,path)
        self.search_json.scan_complete.connect(self.set_ui)
        self.search_json.start()
        #self.set_ui()

        print('thread initialized')


        #if f :
            #    self.recursive_folder(temp_root,f,full_path)

    def set_ui(self) :

        print('thread finished')
        #QTreeWidgetItem(self, [os.path.basename(path).title(),path,'root'])


        #self.recursive_folder(self.tree_root,self.search_json.folders,self.search_json.path)
        self.sortItems(0, Qt.AscendingOrder)
