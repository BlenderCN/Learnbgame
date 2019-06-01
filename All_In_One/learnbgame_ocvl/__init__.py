#  ***** BEGIN GPL LICENSE BLOCK *****
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
#  along with this program; if not, see <http://www.gnu.org/licenses/>
#  and write to the Free Software Foundation, Inc., 51 Franklin Street,
#  Fifth Floor, Boston, MA  02110-1301, USA..
#
#  All rights reserved.
#
#  Contact:      dawid.aniol@teredo.tech    ###
#  Information:  http://teredo.tech         ###
#
#  ***** END GPL LICENSE BLOCK *****
#

import sys
import os


bl_info = {
    "name": "ocvl",
    "author": "Dawid Aniol,OCVL team,Teredo team",
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "Nodes > CustomNodesTree > Add user nodes",
    "description": "Computer vision node-based programming",
    "warning": "",
    "wiki_url": "https://opencv-laboratory.readthedocs.io/en/latest/",
    "tracker_url": "https://github.com/feler404/ocvl/issues",
    "category": "Learnbgame",
}

BASE_DIR = os.path.dirname(__file__)
if __name__ != "ocvl":
    sys.modules["ocvl"] = sys.modules[__name__]


def register():
    from ocvl import logger_conf
    from ocvl.core import node_tree
    from ocvl.core import sockets
    from ocvl.operatores import operatores
    from ocvl.operatores import abc
    from ocvl.core.register_utils import reload_ocvl_modules
    from ocvl.tutorial_engine import operatores as tutorial_engine_operatores
    reload_ocvl_modules()
    node_tree.register()
    sockets.register()
    operatores.register()
    abc.register()
    logger_conf.register()
    tutorial_engine_operatores.register()


def unregister():
    from ocvl.core import node_tree
    from ocvl.core import sockets
    from ocvl.operatores import operatores
    from ocvl.operatores import abc
    from ocvl.tutorial_engine import operatores as tutorial_engine_operatores
    node_tree.unregister()
    sockets.unregister()
    operatores.unregister()
    abc.unregister()
    tutorial_engine_operatores.unregister()


if __name__ == "__main__":

    register()