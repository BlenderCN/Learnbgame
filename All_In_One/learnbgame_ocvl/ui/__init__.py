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

import bpy


from .node import classes_to_unregister as node_classes_to_unregister
from .node import classes as node_classes
from .image_viewer import classes_to_unregister as image_viewer_classes_to_unregister
from .image_viewer import classes as image_viewer_class
from .filebrowser import classes_to_unregister as filebrowser_classes_to_unregister
from .filebrowser import classes as filebrowser_class
from .info import classes_to_unregister as info_classes_to_unregister
from .info import classes as info_classes
from .console import classes_to_unregister as console_classes_to_unregister
from .console import classes as console_clasess
from .text import classes_to_unregister as text_classes_to_unregister
from .text import classes as text_classes
from auth import DEBUG



# https://github.com/trevortomesh/Blender-Python-Learning-Environment/blob/master/BPyLE/lin/blenderPyLE-2.64a-linux64/2.64/scripts/startup/bl_ui/space_info.py


classes_to_unregister = node_classes_to_unregister + image_viewer_classes_to_unregister + filebrowser_classes_to_unregister + info_classes_to_unregister + console_classes_to_unregister + text_classes_to_unregister

classes = node_classes+ image_viewer_class + filebrowser_class + info_classes + console_clasess + text_classes



class OCVLScriptReloadMockOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "script.reload"
    bl_label = "Script Reload Mock"

    def execute(self, context):
        return {'FINISHED'}


def remove_panels():
    for pt in bpy.types.Panel.__subclasses__():
        if pt.bl_space_type == 'NODE_EDITOR':
            if pt.__name__ in ["SvUserPresetsPanel", "SverchokToolsMenu", "SverchokIOLayoutsMenu", "SverchokToolsMenu",
                               "SvTestingPanel", "SverchokIOLayoutsMenu"]:
                bpy.utils.unregister_class(pt)


def register():
    unregister(classes_to_unregister)

    if not DEBUG:
        bpy.utils.register_class(OCVLScriptReloadMockOperator)

    for class_ in classes:
        bpy.utils.register_class(class_)


def unregister(classes=classes):
    if not DEBUG:
        remove_panels()
    for class_ in reversed(classes):
        try:
            bpy.utils.unregister_class(class_)
        except:
            pass