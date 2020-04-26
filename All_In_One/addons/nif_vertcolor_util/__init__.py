#--- ### Header
bl_info = {
           "name": "Niftools - Vertex Utility",
           "description": "Utilities for nif related ",
           "author": "Neomonkeus",
           "version": (1, 0, 0),
           "blender:": (2, 6, 1),
           "api": 35622,
           "location": "Scene Properties Tab -> Niftools Utilities Panel",
           "warning": "not functional, porting from 2.49 series still in progress",
           "wiki_url": (
                        "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/"\
                        "Import-Export/Nif"),
           "tracker_url": (
                           "http://sourceforge.net/tracker/?group_id=149157&atid=776343"),
           "support": "COMMUNITY",
           "category": "Learnbgame",
}

import bpy
import bpy.props

from . import ui, operators, properties

def register():
    properties.register()
    bpy.utils.register_module(__name__)


def unregister():
    properties.unregister()
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()