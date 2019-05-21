# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
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
    "name": "Lib Manager",
    "author": "Christophe Seux, Vincent Gires",
    "description": "Library manager for asset",
    "version": (0, 0, 1),
    "blender": (2, 7, 8),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

if "bpy" in locals():
    import imp
    imp.reload(main_window)
    imp.reload(ui)

import bpy,sys, os, logging

from .functions import read_json


from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication


from . import main_window
from . import ui



class LibManagerModal(bpy.types.Operator):
    bl_idname = "libmanager.modal"
    bl_label = "Lib Manager"

    _timer = None

    def modal(self, context, event):
        wm = context.window_manager
        if self.widget.widget_close :
            logging.debug('cancel modal operator')
            wm.event_timer_remove(self._timer)
            return {"CANCELLED"}
        else:
            logging.debug('process the events for Qt window')
            self.event_loop.processEvents()
            self.app.sendPostedEvents(None, 0)
            self.widget.context = context
            #print('toto')

        return {'PASS_THROUGH'}


    def execute(self, context):
        logging.debug('execute operator')

        self.app = QApplication.instance()
        # instance() gives the possibility to have multiple windows and close it one by one
        if not self.app:
            self.app = QApplication(['blender'])

        self.event_loop = QEventLoop()

        self.widget = main_window.MainWindow()


        logging.debug(self.app)
        logging.debug(self.widget)

        # run modal
        wm = context.window_manager
        self._timer = wm.event_timer_add(1/120, context.window)
        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
