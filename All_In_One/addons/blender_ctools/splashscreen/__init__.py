# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    'name': 'Splash Screen',
    'author': 'chromoly',
    'version': (0, 1),
    'blender': (2, 77, 0),
    'location': '',
    'description': 'Replace default splash screen',
    'warning': 'need PyQt5',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Screen',
}


import functools
import importlib
import os
import queue
import random
import time
import traceback

from PyQt5 import QtGui, QtWidgets, QtCore, QtMultimedia

import bpy

try:
    importlib.reload(utils)
except NameError:
    pass
from .utils import AddonPreferences


EPS = 0.005
TIMER_STEP = 0.01
QT_TIMER_STEP = 0.05
QT_ICON_SIZE = 16
QT_IMAGE_BACK_COLOR = (0, 0, 0)
QT_TOP = True
QT_AUDIO_SUPPORT = ('.mp3', '.flac', '.wav')

if 'first_run' not in globals():
    first_run = True

bl_queue = queue.Queue()
qt_queue = queue.Queue()


# FIXME: リロード後に表示するとQtMultimedia.QMediaPlayer辺りが原因で落ちる


class SplashScreenPreferences(
        AddonPreferences,
        bpy.types.PropertyGroup if '.' in __name__ else
        bpy.types.AddonPreferences):
    bl_idname = __name__

    image_file = bpy.props.StringProperty(
        name='Image File',
        default=os.path.join(os.path.dirname(__file__), 'splash.png'),
        subtype='FILE_PATH',
    )
    sound_directory = bpy.props.StringProperty(
        name='Sound Directory',
        default='',
        subtype='DIR_PATH',
    )
    image_size = bpy.props.IntVectorProperty(
        name='Image Size',
        default=(501, 282),
        size=2,
        min=200
    )
    expand_image = bpy.props.BoolProperty(
        name='Expand Image',
        default=True,
    )
    auto_play = bpy.props.BoolProperty(
        name='Auto Play',
        default=True,
    )

    def draw(self, context):
        layout = self.layout

        column = layout.column()
        split = column.split(0.7)
        col = split.column()
        col.prop(self, 'image_file')
        col.prop(self, 'sound_directory')

        col = split.column()
        row = col.row()
        row.prop(self, 'image_size')
        col.prop(self, 'expand_image')
        col.prop(self, 'auto_play')


class CustomQGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, *args, image_path, expand, **kwargs):
        super().__init__(*args, **kwargs)

        addon_prefs = SplashScreenPreferences.get_instance()

        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setLineWidth(0)
        frame_size = self.frameSize()
        view_port_frame_size = self.viewport().frameSize()
        dx = frame_size.width() - view_port_frame_size.width()
        dy = frame_size.height() - view_port_frame_size.height()
        img_size = addon_prefs.image_size
        self.setMinimumSize(img_size[0] + dx, img_size[1] + dy)

        self.pixmap = None
        self.image_path = image_path
        self.expand = 'expand' if expand else 'scale'  # 'no','scale','expand'
        self.set_image(image_path)

    def resize_image(self):
        if not self.pixmap:
            return
        view_size = self.viewport().size()
        image_size = self.pixmap.size()
        f = view_size.width() / image_size.width()
        if self.expand == 'expand':
            if view_size.height() > image_size.height() * f:
                f = view_size.height() / image_size.height()
        elif self.expand == 'scale':
            if view_size.height() < image_size.height() * f:
                f = view_size.height() / image_size.height()
        else:
            f = 1.0
        self.resetTransform()
        t = self.transform()
        t.scale(f, f)
        self.setTransform(t)

    def resizeEvent(self, event):
        self.resize_image()
        super().resizeEvent(event)

    def set_image(self, path=None):
        import traceback
        if not path:
            return
        try:
            self.pixmap = QtGui.QPixmap(path)
        except:
            traceback.print_exc()
            return
        if self.pixmap.isNull():
            self.pixmap = None
        self.pixmap_item = QtWidgets.QGraphicsPixmapItem(self.pixmap)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.scene.addItem(self.pixmap_item)
        self.setScene(self.scene)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            ls = ['no', 'scale', 'expand']
            i = (ls.index(self.expand) + 1) % 3
            self.expand = ls[i]
            self.resize_image()
            # self.viewport().update()
        elif event.button() == QtCore.Qt.RightButton:
            self.parent().stop_sound()
            self.parent().close()
        else:
            self.parent().play_sound()


class SplashDialog(QtWidgets.QDialog):
    def setupUi(self, Dialog, image_path, expand):
        """自動生成部分"""
        Dialog.setObjectName("Dialog")
        # Dialog.resize(519, 585)
        Dialog.resize(500, 500)
        Dialog.setWindowTitle("Dialog")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")

        # 変更箇所
        self.graphicsView = CustomQGraphicsView(
            Dialog, image_path=image_path, expand=expand)

        brush = QtGui.QBrush(QtGui.QColor(*QT_IMAGE_BACK_COLOR))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.graphicsView.setBackgroundBrush(brush)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        self.horizontalLayout_interaction = QtWidgets.QHBoxLayout()
        self.horizontalLayout_interaction.setObjectName("horizontalLayout_interaction")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_interaction.addItem(spacerItem)
        self.label_interaction = QtWidgets.QLabel(Dialog)
        self.label_interaction.setText("Interaction")
        self.label_interaction.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_interaction.setObjectName("label_interaction")
        self.horizontalLayout_interaction.addWidget(self.label_interaction)
        self.comboBox = QtWidgets.QComboBox(Dialog)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.setItemText(0, "Blender")
        self.comboBox.addItem("")
        self.comboBox.setItemText(1, "3Dsmax")
        self.comboBox.addItem("")
        self.comboBox.setItemText(2, "Blender 2012 Experimental")
        self.comboBox.addItem("")
        self.comboBox.setItemText(3, "Maya")
        self.horizontalLayout_interaction.addWidget(self.comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_interaction)
        self.splitter = QtWidgets.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_links = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_links.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_links.setObjectName("verticalLayout_links")
        self.label_links = QtWidgets.QLabel(self.layoutWidget)
        self.label_links.setText("Links")
        self.label_links.setObjectName("label_links")
        self.verticalLayout_links.addWidget(self.label_links, 0, QtCore.Qt.AlignHCenter)
        self.pushButton_home = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_home.setText("Home site")
        self.pushButton_home.setObjectName("pushButton_home")
        self.verticalLayout_links.addWidget(self.pushButton_home)
        self.pushButton_manual = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_manual.setText("Manual")
        self.pushButton_manual.setObjectName("pushButton_manual")
        self.verticalLayout_links.addWidget(self.pushButton_manual)
        self.pushButton_release = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_release.setText("Release Log")
        self.pushButton_release.setObjectName("pushButton_release")
        self.verticalLayout_links.addWidget(self.pushButton_release)
        self.pushButton_credits = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_credits.setText("Credits")
        self.pushButton_credits.setObjectName("pushButton_credits")
        self.verticalLayout_links.addWidget(self.pushButton_credits)
        self.pushButton_donations = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_donations.setText("Donations")
        self.pushButton_donations.setObjectName("pushButton_donations")
        self.verticalLayout_links.addWidget(self.pushButton_donations)
        self.pushButton_python = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButton_python.setText("Python API")
        self.pushButton_python.setObjectName("pushButton_python")
        self.verticalLayout_links.addWidget(self.pushButton_python)
        self.layoutWidget1 = QtWidgets.QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_recent = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_recent.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_recent.setObjectName("verticalLayout_recent")
        self.label_recent = QtWidgets.QLabel(self.layoutWidget1)
        self.label_recent.setText("Recent")
        self.label_recent.setObjectName("label_recent")
        self.verticalLayout_recent.addWidget(self.label_recent, 0, QtCore.Qt.AlignHCenter)
        self.listWidget = QtWidgets.QListWidget(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setObjectName("listWidget")
        item = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        self.verticalLayout_recent.addWidget(self.listWidget)
        self.horizontalLayout_recent_sub = QtWidgets.QHBoxLayout()
        self.horizontalLayout_recent_sub.setObjectName("horizontalLayout_recent_sub")
        self.pushButton_open = QtWidgets.QPushButton(self.layoutWidget1)
        self.pushButton_open.setText("Open")
        self.pushButton_open.setObjectName("pushButton_open")
        self.horizontalLayout_recent_sub.addWidget(self.pushButton_open)
        self.pushButton_recover = QtWidgets.QPushButton(self.layoutWidget1)
        self.pushButton_recover.setText("Recover Last")
        self.pushButton_recover.setObjectName("pushButton_recover")
        self.horizontalLayout_recent_sub.addWidget(self.pushButton_recover)
        self.verticalLayout_recent.addLayout(self.horizontalLayout_recent_sub)
        self.verticalLayout.addWidget(self.splitter)
        self.horizontalLayout_info = QtWidgets.QHBoxLayout()
        self.horizontalLayout_info.setObjectName("horizontalLayout_info")
        self.label_info_data = QtWidgets.QLabel(Dialog)
        self.label_info_data.setText("Data: 2016-06-05 12:00, Hash: abcdef0, Branch: base")
        self.label_info_data.setObjectName("label_info_data")
        self.horizontalLayout_info.addWidget(self.label_info_data)
        self.verticalLayout.addLayout(self.horizontalLayout_info)

    def __init__(self):
        super().__init__()

        addon_prefs = SplashScreenPreferences.get_instance()
        self.player = QtMultimedia.QMediaPlayer(
            self, QtMultimedia.QMediaPlayer.StreamPlayback)
        self.setupUi(self, addon_prefs.image_file, addon_prefs.expand_image)

        self.init_window_status()
        self.init_preset_menu()
        self.init_link_buttons()
        self.init_recent_buttons()
        self.init_info_label()
        self.init_timer()

        # self.restore_settings()

        self.show()

        if addon_prefs.auto_play:
            self.play_sound()

    def init_window_status(self):
        if QT_TOP:
            self.setWindowFlags(
                QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        app = QtWidgets.QApplication.instance()
        screen_resolution = app.desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        win = bpy.context.window
        self.adjustSize()  # width, heighを再計算
        geom = self.geometry()
        w = geom.width()
        h = geom.height()
        mx = win.x + win.width / 2
        my = height - (win.y + win.height / 2)
        self.setGeometry(mx - w / 2, my - h / 2, w, h)

    def preset_change(self, index):
        path = bpy.utils.resource_path('SYSTEM')

        if index == 0:
            # op = ['wm.appconfig_default', (), {}]
            appconfig_default(bpy.context)
        else:
            if index == 1:
                p = os.path.join(path, 'scripts', 'presets', 'keyconfig',
                                 '3dsmax.py')
            elif index == 2:
                p = os.path.join(path, 'scripts', 'addons_contrib', 'presets',
                                 'keyconfig', 'blender_2012_experimental.py')
            else:
                p = os.path.join(path, 'scripts', 'presets', 'keyconfig',
                                 'maya.py')
            # op = ['wm.appconfig_activate', (), {'filepath': p}]
            appconfig_activate(bpy.context, p)
        # qt_queue.put(op)

    def init_preset_menu(self):
        self.comboBox.activated['int'].connect(self.preset_change)

    def button_link(self, url):
        qt_queue.put(['wm.url_open', (), {'url': url}])
        # self.accept()
        self.close()

    def button_resent(self, index):
        path = self.recent_files[index.row()]
        qt_queue.put(['wm.open_mainfile', (), {'filepath': path}])
        # self.accept()
        self.close()

    def button_open(self):
        qt_queue.put(['wm.open_mainfile', ('INVOKE_DEFAULT',), {}])
        # self.accept()
        self.close()

    def button_recover(self):
        qt_queue.put(['wm.recover_last_session', (), {}])
        # self.accept()
        self.close()

    def init_link_buttons(self):
        icon_dir = os.path.join(os.path.dirname(__file__), 'icons')
        icon_size = QtCore.QSize(QT_ICON_SIZE, QT_ICON_SIZE)

        url = 'http://www.blender.org/foundation/donation-payment/'
        self.pushButton_donations.setToolTip(url)
        self.pushButton_donations.clicked.connect(
            functools.partial(self.button_link, url))

        url = 'http://www.blender.org/about/credits/'
        self.pushButton_credits.setToolTip(url)
        self.pushButton_credits.clicked.connect(
            functools.partial(self.button_link, url))

        url = 'http://wiki.blender.org/index.php/Dev:Ref/Release_Notes/2.77'
        self.pushButton_release.setToolTip(url)
        self.pushButton_release.clicked.connect(
            functools.partial(self.button_link, url))

        url = 'http://www.blender.org/manual'
        self.pushButton_manual.setToolTip(url)
        self.pushButton_manual.clicked.connect(
            functools.partial(self.button_link, url))

        url = 'http://www.blender.org'
        self.pushButton_home.setToolTip(url)
        self.pushButton_home.clicked.connect(
            functools.partial(self.button_link, url))
        icon = QtGui.QIcon(os.path.join(icon_dir, 'icon16_blender.png'))
        self.pushButton_home.setIcon(icon)
        self.pushButton_home.setIconSize(icon_size)

        url = 'http://www.blender.org/documentation/blender_python_api_2_77_1'
        self.pushButton_python.setToolTip(url)
        self.pushButton_python.clicked.connect(
            functools.partial(self.button_link, url))

    def init_recent_buttons(self):
        icon_dir = os.path.join(os.path.dirname(__file__), 'icons')
        icon_size = QtCore.QSize(QT_ICON_SIZE, QT_ICON_SIZE)

        self.listWidget.clear()
        self.recent_files = []
        path = bpy.utils.resource_path('USER')
        path = os.path.join(path, 'config', 'recent-files.txt')
        try:
            with open(path, 'r') as recent:
                for path in recent.readlines():
                    path = path.rstrip('\n')
                    d, f = os.path.split(path)
                    item = QtWidgets.QListWidgetItem(f)
                    item.setText(f)
                    item.setToolTip(path)
                    self.listWidget.addItem(item)
                    self.recent_files.append(path)
        except:
            traceback.print_exc()
            pass
        self.listWidget.activated.connect(self.button_resent)

        self.pushButton_open.clicked.connect(self.button_open)
        icon = QtGui.QIcon(os.path.join(icon_dir, 'icon16_file_folder.png'))
        self.pushButton_open.setIcon(icon)
        self.pushButton_open.setIconSize(icon_size)

        self.pushButton_recover.clicked.connect(self.button_recover)
        icon = QtGui.QIcon(os.path.join(icon_dir, 'icon16_recover_last.png'))
        self.pushButton_recover.setIcon(icon)
        self.pushButton_recover.setIconSize(icon_size)

    def init_info_label(self):
        self.label_info_data.setText(
            'Date: {} {}, Hash: {}, Branch: {}'.format(
                bpy.app.build_date.decode(),
                bpy.app.build_time.decode(),
                bpy.app.build_hash.decode(),
                bpy.app.build_branch.decode()))

    def init_timer(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.timer_event)
        self.timer.start(int(QT_TIMER_STEP * 1000))

    def play_sound(self):
        addon_prefs = SplashScreenPreferences.get_instance()
        files = []
        sound_dir = addon_prefs.sound_directory
        if not sound_dir:
            return
        try:
            for f in os.listdir(sound_dir):
                if f.endswith(QT_AUDIO_SUPPORT):
                    files.append(f)
        except:
            traceback.print_exc()
            return
        if not files:
            return
        path = os.path.join(sound_dir,
                            files[random.randint(0, len(files) - 1)])
        self.url = url = QtCore.QUrl.fromLocalFile(path)
        self.content = content = QtMultimedia.QMediaContent(url)
        self.player.setMedia(content)
        # self.player.setVolume(90)
        self.player.play()

    def stop_sound(self):
        player = self.player
        if player.isAudioAvailable():
            player.stop()

    def eventFilter(self, obj, event):
        # if event.type() == QtCore.QEvent.WindowDeactivate:
        #     self.close()
        #     return True
        # if event.type() == QtCore.QEvent.MouseMove:
        #     return True
        return False

    def keyPressEvent(self, event):
        if event.key() in {QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return}:
            self.accept()
        elif event.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def accept(self):
        # self.stop_sound()
        # # self.save_settings()
        # qt_queue.put(None)
        # super().accept()
        self.close()

    def reject(self):
        # self.stop_sound()
        # # self.save_settings()
        # qt_queue.put(None)
        # super().reject()
        self.close()

    def closeEvent(self, event):
        # print('closeEvent')
        # self.stop_sound()
        # self.save_settings()
        qt_queue.put(None)

    # 未使用
    # def save_settings(self):
    #     p = os.path.join(os.path.dirname(__file__), 'settings.dat')
    #     settings = QtCore.QSettings(p, QtCore.QSettings.IniFormat)
    #     settings.setIniCodec('utf-8')
    #     settings.setValue('geometry', self.saveGeometry())
    #
    # def restore_settings(self):
    #     p = os.path.join(os.path.dirname(__file__), 'settings.dat')
    #     settings = QtCore.QSettings(p, QtCore.QSettings.IniFormat)
    #     settings.setIniCodec('utf-8')
    #     geom = settings.value('geometry')
    #     if geom is not None:
    #         self.restoreGeometry(geom)

    def timer_event(self):
        try:
            while True:
                item = bl_queue.get_nowait()
                if item is None:
                    self.close()
                    break
        except queue.Empty:
            return


def execute_preset(context, filepath, menu_idname):
    """scripts/startup/bl_operators/presets.py: 202: class ExecutePreest"""

    # change the menu title to the most recently chosen option
    preset_class = getattr(bpy.types, menu_idname)
    preset_class.bl_label = bpy.path.display_name(os.path.basename(filepath))

    ext = os.path.splitext(filepath)[1].lower()

    # execute the preset using script.python_file_run
    if ext == ".py":
        # bpy.ops.script.python_file_run(filepath=filepath)
        try:
            with open(filepath, 'r') as f:
                txt = f.read()
                exec(txt)
        except:
            traceback.print_exc()
    elif ext == ".xml":
        import rna_xml
        rna_xml.xml_file_run(context,
                             filepath,
                             preset_class.preset_xml_map)
    else:
        # self.report({'ERROR'}, "unknown filetype: %r" % ext)
        return {'CANCELLED'}

    return {'FINISHED'}


def appconfig_default(context):
    """scripts/startup/bl_operators/wm.py:
    1428: class WM_OT_appconfig_default

    上記のオペレータを実行する際に以下のエラーが発生するのでこの関数で置換する
    RuntimeError: Operator bpy.ops.script.python_file_run.poll() failed,
                  context is incorrect
    """
    wm = context.window_manager
    wm.keyconfigs.active = wm.keyconfigs.default
    filepath = os.path.join(bpy.utils.preset_paths("interaction")[0],
                            "blender.py")
    if os.path.exists(filepath):
        # bpy.ops.script.execute_preset(
        #     filepath=filepath, menu_idname="USERPREF_MT_interaction_presets")
        execute_preset(context, filepath, 'USERPREF_MT_interaction_presets')


def appconfig_activate(context, filepath):
    """scripts/startup/bl_operators/wm.py:
    1428: class WM_OT_appconfig_activate

    上記のオペレータを実行する際に以下のエラーが発生するのでこの関数で置換する
    RuntimeError: Operator bpy.ops.script.python_file_run.poll() failed,
                  context is incorrect
    """

    bpy.utils.keyconfig_set(filepath)

    filepath = filepath.replace("keyconfig", "interaction")

    if os.path.exists(filepath):
        # bpy.ops.script.execute_preset(
        #     filepath=filepath, menu_idname="USERPREF_MT_interaction_presets")
        execute_preset(context, filepath, 'USERPREF_MT_interaction_presets')


class QTSplash(bpy.types.Operator):
    bl_idname = 'wm.splash_qt'
    bl_label = 'Qt Splash Screen'

    bl_options = {'REGISTER'}

    timer = None

    @classmethod
    def init_queue(cls):
        global bl_queue, qt_queue
        bl_queue = queue.Queue()
        qt_queue = queue.Queue()

    @classmethod
    def timer_add(cls, context):
        if not cls.timer:
            wm = context.window_manager
            cls.timer = wm.event_timer_add(TIMER_STEP, context.window)

    @classmethod
    def timer_remove(cls, context):
        if cls.timer:
            wm = context.window_manager
            wm.event_timer_remove(cls.timer)
            cls.timer = None

    @classmethod
    def cancel_(cls, context):
        # wm.open_mainfile()の際にself.cancel()だとエラー
        cls.timer_remove(context)
        cls.win.close()
        # cls.app.quit()

    def cancel(self, context):
        self.cancel_(context)

    def modal(self, context, event):
        t = time.perf_counter()

        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE', 'MIDDLEMOUSE'}:
            if event.value == 'PRESS':
                self.__class__.win.close()
                self.cancel_(context)
                return {'CANCELLED'}

        if event.type != 'TIMER' or t - self.prev_time + EPS < TIMER_STEP:
            return {'PASS_THROUGH'}

        self.prev_time = t

        self.event_loop.processEvents()

        try:
            while True:
                item = qt_queue.get_nowait()
                if item is None:
                    QTSplash.cancel_(context)
                    return {'CANCELLED'}
                elif isinstance(item, list):
                    op, args, kwargs = item
                    if not {True, False} & set(args):
                        args = tuple(args) + (True,)
                    eval('bpy.ops.' + op)(*args, **kwargs)

        except queue.Empty:
            return {'PASS_THROUGH'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        """
        :param context: bpy.types.Context
        :param event: bpy.types.Event
        """

        cls = self.__class__

        wm = context.window_manager
        wm.modal_handler_add(self)
        self.timer_add(context)
        self.prev_time = time.perf_counter()

        self.init_queue()
        app = QtWidgets.QApplication.instance()
        if not app:
            app = QtWidgets.QApplication(['blender'])
        cls.app = app
        app.setWheelScrollLines(1)

        cls.event_loop = QtCore.QEventLoop()

        cls.win = SplashDialog()
        app.installEventFilter(cls.win)

        return {'RUNNING_MODAL'}


@bpy.app.handlers.persistent
def scene_update_pre(scene):
    global first_run
    bpy.app.handlers.scene_update_pre.remove(scene_update_pre)
    bpy.ops.wm.splash_qt('INVOKE_DEFAULT')

def menu_item(self, context):
    layout = self.layout.column()
    # layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator('wm.splash_qt', icon='BLENDER')


classes = [
    SplashScreenPreferences,
    QTSplash,
]

show_splash = False


def register():
    global show_splash, first_run
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.INFO_MT_help.append(menu_item)
    if first_run:
        bpy.app.handlers.scene_update_pre.append(scene_update_pre)
        first_run = False

    U = bpy.context.user_preferences
    show_splash = U.view.show_splash
    U.view.show_splash = False


def unregister():
    bpy.types.INFO_MT_help.remove(menu_item)
    for cls in classes[::-1]:
        bpy.utils.unregister_class(cls)

    U = bpy.context.user_preferences
    U.view.show_splash = show_splash


if __name__ == '__main__':
    register()
