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
from .BtnFolder import BtnFolder

from os.path import join,dirname,basename,realpath,splitext
from os import listdir
from ..functions import get_css,icon_path,clear_layout,read_json,image_path

import bpy,os,importlib
import re
import subprocess

working_dir = dirname(dirname(realpath(__file__)))

class Batch(QVBoxLayout) :
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


        self.batch_folder = join(working_dir,'batch')
        batches = [f for f in listdir(self.batch_folder)]

        #CMD
        self.cbox_cmd = ComboBox()
        self.cbox_cmd.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.cbox_cmd.setFixedHeight(22)
        self.cbox_cmd.setStyleSheet(get_css("ComboBox"))
        for batch in sorted(batches):
            self.cbox_cmd.addItem(batch)

        self.cmd_row = QHBoxLayout()
        self.cmd_row.addWidget(Label(text='Cmd :'))
        self.cmd_row.addWidget(self.cbox_cmd)

        '''
        # Folder
        self.folder = LineEdit()
        self.folder_row = QHBoxLayout()
        self.folder_row.addWidget(Label(text='Folder :'))
        self.folder_row.addWidget(self.folder)

        # Category
        self.category = LineEdit()
        self.category_row = QHBoxLayout()
        self.category_row.addWidget(Label(text='Category :'))
        self.category_row.addWidget(self.category)
        '''
        self.template_folder = join(working_dir,'templates')
        templates = [f for f in listdir(self.template_folder)]

        # template
        self.cbox_template = ComboBox()
        self.cbox_template.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.cbox_template.setFixedHeight(22)
        for template in sorted(templates):
            self.cbox_template.addItem(template)

        self.template_row = QHBoxLayout()
        self.template_row.addWidget(Label(text='Templates :'))
        self.template_row.addWidget(self.cbox_template)


        # Folder
        self.folder = LineEdit()
        self.btn_folder = BtnFolder(self.folder)
        self.folder_row = QHBoxLayout()
        self.folder_row.addWidget(Label(text='Folder :'))
        self.folder_row.addWidget(self.folder)
        self.folder_row.addWidget(self.btn_folder)

        # Option
        self.expression = LineEdit()
        self.expression.setText('[\d][\d][\d]')
        self.extension = LineEdit()
        self.extension.setText('blend')
        self.last_version_only = CheckBox(' Last only')

        self.option_row = QHBoxLayout()
        self.option_row.addWidget(Label(text='Expression :'))
        self.option_row.addWidget(self.expression)
        self.option_row.addWidget(self.extension)
        self.option_row.addWidget(self.last_version_only)


        # Execute
        self.btn_execute = PushButton(text= 'Execute')
        self.btn_execute.clicked.connect(self.execute_batch)

        verticalSpacer = QSpacerItem(20, 16, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # add widgets to main layout
        self.mainLayout.addLayout(self.cmd_row)
        self.mainLayout.addLayout(self.template_row)
        self.mainLayout.addLayout(self.folder_row)
        self.mainLayout.addLayout(self.option_row)
        self.mainLayout.addWidget(self.btn_execute)
        #self.mainLayout.addLayout(self.category_row)

        self.mainLayout.addItem(verticalSpacer)


        self.addLayout(self.mainLayout)

    def execute_batch(self) :
        folder = os.path.normpath(self.folder.text())
        expression = self.expression.text()
        extension = self.extension.text()

        print('folder',folder)

        files= []
        if not self.last_version_only.isChecked() :
            files = []
            for root,folders,files in os.walk(folder) :
                for f in files :
                    name,ext= splitext(f)
                    if re.search(expression,name) and ext == '.'+extension :
                        files.append(f)
        else :
            files_version = {}
            for root,folders,files in os.walk(folder) :
                for f in files :
                    name,ext= splitext(f)
                    search = re.search(expression,name)
                    if search and ext == '.'+extension :
                        basename = search.string.replace(search.group(0),'')

                        if not files_version.get(basename):
                            files_version[basename] =[]

                        files_version[basename].append(join(root,f))


            for f,versions in files_version.items() :
                files.append(sorted(versions)[-1])

        print(files)

        batch = join(self.batch_folder,self.cbox_cmd.currentText())
        template = join(self.template_folder,self.cbox_template.currentText())

        print(template,os.path.exists(template))

        blender_path = bpy.app.binary_path

        args={
            'files' : files,
            'folder' : folder
        }

        subprocess.call([blender_path,template,'-p','4096','0','0','0','--python',batch,'--',str(args)])

        #batch_fill_lib(template,files,folder = None,category = None)
        #from

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
