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

# <pep8 compliant>

bl_info = {
    "name": 'b2rex',
    "author": 'Invi, Caedes',
    "blender": (2, 5, 7),
    "api": 35622,
    "version": (0, 8, 0),
    "location": 'Tools window > Scene panel',
    "warning": '',
    "description": 'Connect to opensim and realxtend servers',
    "wiki_url": 'https://sim.lorea.org/pg/pages/view/438/',
    "support": 'COMMUNITY',
    "tracker_url": 'https://github.com/b2rex/b2rex',
    "category": "Learnbgame"
}

import sys
import traceback
from .tools.siminfo import GridInfo
from .importer import Importer
from .tools.logger import logger

ERROR = 0
OK = 1
IMMEDIATE = 2

safe_mode = True

if sys.version_info[0] == 2:
    import Blender
    from .b24 import hacks
    from .b24 import editor
else:
    from bpy.props import PointerProperty
    from .b25 import editor
    from .b25.ops import Connect, Export, Import, Settings, SetLogLevel, Redraw
    from .b25.ops import Upload, ExportUpload, Sync, Check, ProcessQueue
    from .b25.ops import RequestAsset, Section, B2RexStartGame
    from .b25.panels.main import ConnectionPanel
    from .b25.panels.menu import Menu
    from .b25.panels.text import B2RexTextMenu
    from .b25.panels.object import ObjectPropertiesPanel
    from .b25.panels.objectdbg import ObjectDebugPanel

    from .b25.properties import B2RexRegions, B2RexProps, B2RexTextProps
    from .b25.properties import B2RexObjectProps, B2RexMaterialProps
    from .b25.properties import B2RexMeshProps, B2RexTextureProps
    from .b25.properties import B2RexImageProps, B2RexChatLine
    from .b25.logic import B2RexState, B2RexSensor, B2RexActuator, B2RexFsm
    from .b25.logic import FsmActuatorTypeAction, FsmAction
    from .b25.app import B2Rex

import bpy

_oldheader_ = None

def register():
    global _oldheader_
    if hasattr(bpy.utils, "register_module"):
        bpy.utils.register_module(__name__)

    bpy.types.Scene.b2rex_props = PointerProperty(type=B2RexProps, name="b2rex props")
    bpy.types.Object.opensim = PointerProperty(type=B2RexObjectProps,
                                               name="b2rex object props")
    bpy.types.Mesh.opensim = PointerProperty(type=B2RexMeshProps,
                                               name="b2rex object props")
    bpy.types.Text.opensim = PointerProperty(type=B2RexTextProps,
                                               name="b2rex text props")
    bpy.types.Material.opensim = PointerProperty(type=B2RexMaterialProps,
                                               name="b2rex object props")
    bpy.types.Texture.opensim = PointerProperty(type=B2RexTextureProps,
                                               name="b2rex object props")
    bpy.types.Image.opensim = PointerProperty(type=B2RexImageProps,
                                               name="b2rex object props")
    bpy.b2rex_session = B2Rex(bpy.context.scene)
    if hasattr(bpy.types, 'INFO_HT_header'):
        _oldheader_ = bpy.types.INFO_HT_header
        if hasattr(bpy.utils, "unregister_class"):
            bpy.utils.unregister_class( bpy.types.INFO_HT_header )
        else:
            bpy.types.unregister( bpy.types.INFO_HT_header )
    if hasattr(bpy.types, 'INFO_HT_myheader'):
        if hasattr(bpy.utils, "unregister_class"):
            bpy.utils.unregister_class( bpy.types.INFO_HT_myheader )
        else:
            bpy.types.unregister( bpy.types.INFO_HT_myheader )


#    register_keymaps()

def unregister():
    logger.debug("byez!-")
    del bpy.types.Scene.b2rex_props
    del bpy.b2rex_session
    # XXX are we sure we want to do this?
    del bpy.types.Object.opensim
    del bpy.types.Mesh.opensim
    del bpy.types.Material.opensim
    del bpy.types.Texture.opensim
    del bpy.types.Image.opensim
    bpy.utils.register_class( _oldheader_ )
    #testthread.running = False
#    unregister_keymaps()


if __name__ == "__main__":
    register()
