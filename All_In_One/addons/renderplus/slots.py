# ------------------------------------------------------------------------------
# LICENSE
# ------------------------------------------------------------------------------
# Render+ - Blender addon
# (c) Copyright Diego Garcia Gangl (januz) - 2014, 2015
# <diego@sinestesia.co>
# ------------------------------------------------------------------------------
# This file is part of Render+
#
# Render+ is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# ------------------------------------------------------------------------------

import logging

import bpy


# ------------------------------------------------------------------------------
#  INTERNAL VARIABLES
# ------------------------------------------------------------------------------

# Logging
log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
#  CONVENIENCE FUNCTIONS
# ------------------------------------------------------------------------------

def update_list():
    """ Update slot list (used after rendering)"""

    settings = bpy.context.scene.renderplus

    try:
        settings.active_slot = bpy.data.images[
            'Render Result'].render_slots.active_index
        settings.slots[settings.active_slot].is_used = True
    except KeyError:
        # This happens when batch rendering
        pass


def generate_list():
    """ Generate slot list for this scene """

    settings = bpy.context.scene.renderplus
    log.debug('Generating slots list')

    for i in range(0, 8):
        settings.slots.add()
        settings.slots[i].id = i
        settings.slots[i].name = 'Slot'
        settings.slots[i].is_used = False


# ------------------------------------------------------------------------------
#  OPERATORS
# ------------------------------------------------------------------------------

class RP_changeSlot(bpy.types.Operator):

    """ Change the active renderslot """

    bl_idname = "renderplus.change_slot"
    bl_label = "Change render slot"

    index = bpy.props.IntProperty(min=0, max=8, default=0)

    def execute(self, context):
        context.scene.renderplus.active_slot = self.index
        bpy.data.images['Render Result'].render_slots.active_index = self.index

        log.debug('Active slot change to: ' + str(self.index))

        return {'FINISHED'}


class RP_setSlotName(bpy.types.Operator):

    """ Change the active renderslot """

    bl_idname = 'renderplus.set_slot_name'
    bl_label = 'Change render slot name'

    name = bpy.props.StringProperty(default='Slot')

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'name', text='Name')

    def execute(self, context):
        index = context.scene.renderplus.active_slot
        context.scene.renderplus.slots[index].name = self.name
        return {'FINISHED'}
