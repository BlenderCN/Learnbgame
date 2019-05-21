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

# Based on paint select by Kjartan
# http://blenderartists.org/forum/showthread.php?383998

import bpy
from bpy.props import BoolProperty


class PaintSelect(bpy.types.Operator):
    bl_idname = "view3d.paint_select"
    bl_label = "Paint Select"
    bl_options = {'REGISTER', 'UNDO'}

    deselect = BoolProperty(name="Deselect",
                            default=False)

    def modal(self, context, event):
        if self.deselect:
            bpy.ops.view3d.select('INVOKE_DEFAULT',
                                  extend=False,
                                  deselect=True,
                                  toggle=True)
        else:
            bpy.ops.view3d.select('INVOKE_DEFAULT',
                                  extend=True,
                                  deselect=False)
        if event.value == 'RELEASE':
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
