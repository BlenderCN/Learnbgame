"""
Copyright (C) 2017 Bricks Brought to Life
http://bblanimation.com/
chris@bblanimation.com

Created by Christopher Gearhart

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# system imports
import bpy
from ..functions import *
from bpy.app.handlers import persistent


@persistent
def handle_selections(junk=None):
    scn = bpy.context.scene
    obj = bpy.context.view_layer.objects.active if b280() else scn.objects.active
    # # if scn.layers changes and active object is no longer visible, set scn.aglist_index to -1
    # if scn.assemblMe_last_layers != str(list(scn.layers)):
    #     scn.assemblMe_last_layers = str(list(scn.layers))
    #     curCollVisible = False
    #     if scn.aglist_index != -1:
    #         ag0 = scn.aglist[scn.aglist_index]
    #         curCollVisible,_ = isCollectionVisible(scn, ag0)
    #     if not curCollVisible or scn.aglist_index == -1:
    #         setIndex = False
    #         for i,ag in enumerate(scn.aglist):
    #             if i != scn.aglist_index:
    #                 nextCollVisible,obj = isCollectionVisible(scn, ag)
    #                 if nextCollVisible and obj == obj:
    #                     scn.aglist_index = i
    #                     setIndex = True
    #                     break
    #         if not setIndex:
    #             scn.aglist_index = -1
    # select and make source or LEGO model active if scn.aglist_index changes
    if scn.assemblMe_last_aglist_index != scn.aglist_index and scn.aglist_index != -1:
        scn.assemblMe_last_aglist_index = scn.aglist_index
        ag = scn.aglist[scn.aglist_index]
        coll = ag.collection
        if coll is not None and len(coll.objects) > 0:
            select(list(coll.objects), active=coll.objects[0], only=True)
            scn.assemblMe_last_active_object_name = obj.name
    # open LEGO model settings for active object if active object changes
    elif obj and scn.assemblMe_last_active_object_name != obj.name and (scn.aglist_index == -1 or scn.aglist[scn.aglist_index].collection is not None):# and obj.type == "MESH":
        scn.assemblMe_last_active_object_name = obj.name
        # do nothing, because the active aglist index refers to this collection
        if scn.aglist_index != -1 and scn.aglist[scn.aglist_index].collection in (obj.users_collection if b280() else obj.users_group):
            return 0.2
        # attempt to switch aglist index if one of them refers to this collection
        for i in range(len(scn.aglist)):
            ag = scn.aglist[i]
            if ag.collection in (obj.users_collection if b280() else obj.users_group):
                scn.aglist_index = i
                scn.assemblMe_last_aglist_index = scn.aglist_index
                tag_redraw_areas("VIEW_3D")
                return 0.2
        scn.aglist_index = -1
    return 0.2


@persistent
@blender_version_wrapper('>=','2.80')
def register_assemblme_timers(scn):
    timer_fns = (handle_selections,)
    for timer_fn in timer_fns:
        if not bpy.app.timers.is_registered(timer_fn):
            bpy.app.timers.register(timer_fn)
