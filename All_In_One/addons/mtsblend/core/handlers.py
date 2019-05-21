# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
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
# ***** END GPL LICENSE BLOCK *****

import bpy

from bpy.app.handlers import persistent

from ..nodes import MitsubaNodeManager
from ..export.geometry import GeometryExporter
from ..outputs import MtsLog


@persistent
def mts_scene_update(context):
    if bpy.data.objects.is_updated:
        for ob in bpy.data.objects:
            if ob is None:
                continue

            # only flag as updated if either modifiers or
            # mesh data is updated
            if ob.is_updated_data or (ob.data is not None and ob.data.is_updated):
                GeometryExporter.KnownModifiedObjects.add(ob)

    if bpy.data.node_groups.is_updated:
        context.mitsuba_nodegroups.refresh()


@persistent
def mts_node_manager_lock(context):
    MitsubaNodeManager.lock()


@persistent
def mts_scene_load(context):
    # clear known list on scene load and unlock node manager
    GeometryExporter.KnownExportedObjects = set()
    MitsubaNodeManager.unlock()

if hasattr(bpy.app, 'handlers') and hasattr(bpy.app.handlers, 'scene_update_post'):
    bpy.app.handlers.scene_update_post.append(mts_scene_update)
    bpy.app.handlers.load_pre.append(mts_node_manager_lock)
    bpy.app.handlers.load_post.append(mts_scene_load)
    MtsLog('Installed scene post-update handler')
