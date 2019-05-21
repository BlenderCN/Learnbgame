# -*- coding: utf-8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.5 Extensions Framework
# --------------------------------------------------------------------------
#
# Authors:
# Doug Hammond
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
import bpy

from .validate import Logician

class EF_OT_msg(bpy.types.Operator):
    """An operator to show simple messages in the UI"""
    bl_idname = 'ef.msg'
    bl_label = 'Show UI Message'
    msg_type = bpy.props.StringProperty(default='INFO')
    msg_text = bpy.props.StringProperty(default='')
    def execute(self, context):
        self.report({self.properties.msg_type}, self.properties.msg_text)
        return {'FINISHED'}

def _get_item_from_context(context, path):
    """Utility to get an object when the path to it is known:
    _get_item_from_context(context, ['a','b','c']) returns
    context.a.b.c
    No error checking is performed other than checking that context
    is not None. Exceptions caused by invalid path should be caught in
    the calling code.

    """

    if context is not None:
        for p in path:
            context = getattr(context, p)
    return context

