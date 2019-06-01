#
# V-Ray/Blender
#
# http://www.chaosgroup.com
#
# Author: Andrei Izrantcev
# E-Mail: andrei.izrantcev@chaosgroup.com
#
# This program is free software; you can redistribute it and/or
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.
#

import bpy


def AddEvent(event, func):
    if func not in event:
        event.append(func)

def DelEvent(event, func):
    if func in event:
        event.remove(func)


@bpy.app.handlers.persistent
def dr_nodes_store(e):
    bpy.ops.vray.dr_nodes_save()


@bpy.app.handlers.persistent
def dr_nodes_restore(e):
    bpy.ops.vray.dr_nodes_load()


def register():
    AddEvent(bpy.app.handlers.save_post, dr_nodes_store)
    AddEvent(bpy.app.handlers.load_post, dr_nodes_restore)


def unregister():
    DelEvent(bpy.app.handlers.save_post, dr_nodes_store)
    DelEvent(bpy.app.handlers.load_post, dr_nodes_restore)
