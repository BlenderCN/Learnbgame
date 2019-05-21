'''
Copyright (C) 2015 Peter Noble
peter@noblesque.org.uk

Created by Peter Noble

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
'''

bl_info = {
    "name": "InAIte",
    "description": "(Prototype) Simulate crowds of agents in Blender!",
    "author": "Peter Noble",
    "version": (0, 1),
    "blender": (2, 76, 0),
    "location": "Properties > Scene and Node Editor",
    "category": "Animation",
    "warning": "Extremely experimental! Press save regularly"
}

import bpy
import random
from bpy.props import IntProperty, EnumProperty, CollectionProperty
from bpy.props import PointerProperty, BoolProperty, StringProperty
from bpy.types import PropertyGroup, UIList, Panel, Operator


# =============== GROUPS LIST START ===============#


class SCENE_UL_group(UIList):
    """for drawing each row"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=str(item.name))
            layout.prop(item, "type", text="")
            # layout.prop_search(item, "type", bpy.data, "actions", text="")
            # this draws each row in the list. Each line is a widget
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
            # no idea when this is actually used


class SCENE_OT_group_populate(Operator):
    bl_idname = "scene.iai_groups_populate"
    bl_label = "Populate group list"

    def execute(self, context):
        groups = []
        toRemove = []
        sce = context.scene
        for f in range(len(sce.iai_groups.coll)):
            name = context.scene.iai_groups.coll[f].name
            if name not in groups:
                if name in [str(x.group) for x in sce.iai_agents.coll]:
                    groups.append(context.scene.iai_groups.coll[f].name)
            else:
                toRemove.append(f)
        for f in reversed(toRemove):
            context.scene.iai_groups.coll.remove(f)
        for agent in context.scene.iai_agents.coll:
            if str(agent.group) not in groups:
                groups.append(str(agent.group))
                item = context.scene.iai_groups.coll.add()
                item.name = str(agent.group)
                item.type = 'NONE'
        return {'FINISHED'}

# TODO  needs list clean up adding


class SCENE_OT_group_remove(Operator):
    """NOT USED NEEDS REMOVING ONCE THE POPULATE KEEPS THE LIST CLEAR"""
    bl_idname = "scene.iai_groups_remove"
    bl_label = "Remove"

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.iai_groups.coll) > s.iai_groups.index >= 0

    def execute(self, context):
        s = context.scene
        s.iai_groups.coll.remove(s.iai_groups.index)
        if s.iai_groups.index > 0:
            s.iai_groups.index -= 1
        return {'FINISHED'}


class SCENE_OT_group_move(Operator):
    """NEEDS TO BE REMOVED ONCE POPULATE IS WORKING"""
    bl_idname = "scene.iai_groups_move"
    bl_label = "Move"

    direction = EnumProperty(items=(
        ('UP', "Up", "Move up"),
        ('DOWN', "Down", "Move down"))
    )

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.iai_groups.coll) > s.iai_groups.index >= 0

    def execute(self, context):
        s = context.scene
        d = -1 if self.direction == 'UP' else 1
        new_index = (s.iai_groups.index + d) % len(s.iai_groups.coll)
        s.iai_groups.coll.move(s.iai_groups.index, new_index)
        s.iai_groups.index = new_index
        return {'FINISHED'}

# =============== GROUPS LIST END ===============#

# =============== AGENTS LIST START ===============#


class SCENE_UL_agents(UIList):
    """for drawing each row"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.name in context.scene.objects:
                ic = 'OBJECT_DATA'
            else:
                ic = 'ERROR'
            layout.prop_search(item, "name", bpy.data, "objects")
            layout.prop(item, "group", text="")
            typ = [g.type for g in bpy.context.scene.iai_groups.coll
                   if int(g.name) == item.group][0]
            layout.label(text=typ)
            # this draws each row in the list. Each line is a widget
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
            # no idea when this is actually used


class SCENE_OT_iai_agents_populate(Operator):
    bl_idname = "scene.iai_agents_populate"
    bl_label = "Populate iai agents list"

    def findNext(self):
        g = [x.group for x in bpy.context.scene.iai_agents.coll]
        i = 1
        while True:
            if i not in g:
                return i
            else:
                i += 1

    def execute(self, context):
        setiaiBrains()

        ag = [x.name for x in bpy.context.scene.iai_agents.coll]

        if bpy.context.scene.iai_agents_default.startType == "Next":
            group = self.findNext()
        else:
            group = bpy.context.scene.iai_agents_default.setno

        for i in bpy.context.selected_objects:
            if i.name not in ag:
                item = context.scene.iai_agents.coll.add()
                item.name = i.name
                item.group = group
                if bpy.context.scene.iai_agents_default.contType == "Inc":
                    if context.scene.iai_agents_default.startType == "Next":
                        group = self.findNext()
                    else:
                        bpy.context.scene.iai_agents_default.setno += 1
                        group = bpy.context.scene.iai_agents_default.setno
                item.type = 'NONE'
        bpy.ops.scene.iai_groups_populate()
        return {'FINISHED'}


class SCENE_OT_agent_remove(Operator):
    bl_idname = "scene.iai_agents_remove"
    bl_label = "Remove"

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.iai_agents.coll) > s.iai_agents.index >= 0

    def execute(self, context):
        s = context.scene
        s.iai_agents.coll.remove(s.iai_agents.index)
        if s.iai_agents.index > 0:
            s.iai_agents.index -= 1
        return {'FINISHED'}


class SCENE_OT_agent_move(Operator):
    bl_idname = "scene.iai_agents_move"
    bl_label = "Move"

    direction = EnumProperty(items=(
        ('UP', "Up", "Move up"),
        ('DOWN', "Down", "Move down"))
    )

    @classmethod
    def poll(cls, context):
        s = context.scene
        return len(s.iai_agents.coll) > s.iai_agents.index >= 0

    def execute(self, context):
        s = context.scene
        d = -1 if self.direction == 'UP' else 1
        new_index = (s.iai_agents.index + d) % len(s.iai_agents.coll)
        s.iai_agents.coll.move(s.iai_agents.index, new_index)
        s.iai_agents.index = new_index
        return {'FINISHED'}


# =============== AGENTS LIST END ===============#

# =============== SELECTED LIST START ===============#


class SCENE_UL_selected(UIList):
    """for drawing each row"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.name in context.scene.objects:
                ic = 'OBJECT_DATA'
            else:
                ic = 'ERROR'
            layout.prop(item, "name", text="", emboss=False, icon=ic)
            # this draws each row in the list. Each line is a widget
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
            # no idea when this is actually used


class SCENE_OT_iai_selected_populate(Operator):
    bl_idname = "scene.iai_selected_populate"
    bl_label = "See group"

    def execute(self, context):
        self.group = bpy.context.scene.iai_groups
        self.group_selected = bpy.context.scene.iai_agents_selected
        self.group_selected.coll.clear()

        for i in bpy.context.scene.iai_agents.coll:
            if self.group.index < len(self.group.coll):
                if i.group == int(self.group.coll[self.group.index].name):
                    item = context.scene.iai_agents_selected.coll.add()
                    item.name = i.name
        return {'FINISHED'}

# =============== SELECTED LIST END ===============#

# =============== SIMULATION START ===============#


class SCENE_OT_iai_start(Operator):
    bl_idname = "scene.iai_start"
    bl_label = "Start simulation"

    def execute(self, context):
        context.scene.frame_current = context.scene.frame_start
        global sim
        if "sim" in globals():
            sim.stopFrameHandler()
            del sim
        sim = Simulation()
        sim.actions()
        """for ag in bpy.context.scene.iai_agents.coll:
            sim.newagent(ag.name)"""
        sim.createAgents(bpy.context.scene.iai_agents.coll)
        sim.startFrameHandler()
        return {'FINISHED'}


class SCENE_OT_iai_stop(Operator):
    bl_idname = "scene.iai_stop"
    bl_label = "Unregister the advance frame handler"

    def execute(self, context):
        global sim
        if "sim" in globals():
            sim.stopFrameHandler()
        return {'FINISHED'}

# =============== SIMULATION END ===============#


global initialised
initialised = False


class SCENE_PT_inaite(Panel):
    """Creates inaite Panel in the scene properties window. The first panel
    that this add-on creates"""
    bl_label = "InAIte"
    bl_idname = "SCENE_PT_inaite"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        global initialised
        if not initialised:
            initialised = True
            initialise()
        layout = self.layout
        sce = context.scene

        row = layout.row()
        row.template_list("SCENE_UL_group", "", sce.iai_groups,
                          "coll", sce.iai_groups, "index")

        col = row.column()
        sub = col.column(True)
        sub.operator(SCENE_OT_group_populate.bl_idname, text="", icon="ZOOMIN")

        sub = col.column(True)
        sub.separator()
        blid_gm = SCENE_OT_group_move.bl_idname
        sub.operator(blid_gm, text="", icon="TRIA_UP").direction = 'UP'
        sub.operator(blid_gm, text="", icon="TRIA_DOWN").direction = 'DOWN'
        sub.separator()
        blid_sp = SCENE_OT_iai_selected_populate.bl_idname
        sub.operator(blid_sp, text="", icon="PLUS")

        #####

        layout.label(text="Selected Agents")
        layout.template_list("SCENE_UL_selected", "", sce.iai_agents_selected,
                             "coll", sce.iai_agents_selected, "index")

        #####

        layout.label(text="All agents:")
        row = layout.row()
        row.template_list("SCENE_UL_agents", "", sce.iai_agents,
                          "coll", sce.iai_agents, "index")

        col = row.column()
        sub = col.column(True)
        blid_ap = SCENE_OT_iai_agents_populate.bl_idname
        sub.operator(blid_ap, text="", icon="ZOOMIN")
        blid_ar = SCENE_OT_agent_remove.bl_idname
        sub.operator(blid_ar, text="", icon="ZOOMOUT")

        sub = col.column(True)
        sub.separator()
        blid_am = SCENE_OT_agent_move.bl_idname
        sub.operator(blid_am, text="", icon="TRIA_UP").direction = 'UP'
        sub.operator(blid_am, text="", icon="TRIA_DOWN").direction = 'DOWN'

        default = bpy.context.scene.iai_agents_default
        layout.label(text="Default agents group:")

        row = layout.row()
        row.prop(default, "startType", expand=True)
        row.prop(default, "setno", text="")

        row = layout.row()
        row.prop(default, "contType", expand=True)

        row = layout.row()
        row.operator(SCENE_OT_iai_start.bl_idname)
        row.operator(SCENE_OT_iai_stop.bl_idname)

        row = layout.row()
        row.label(text="ALWAYS save before pressing the start button!")


def register():
    """Called by Blender to setup the script. Analogous to the constructor of
    an object but for the add-on instead"""
    bpy.utils.register_module(__name__)
    # I think this registers the SCENE_PT_inaite class...
    # ...or maybe all the classes in the file?

    global action_register
    from .iai_actions import action_register
    global action_unregister
    from .iai_actions import action_unregister

    global event_register
    from .iai_events import event_register
    global event_unregister
    from .iai_events import event_unregister

    from .iai_blenderData import registerTypes

    global setiaiBrains
    from .iai_blenderData import setiaiBrains

    global iai_bpyNodes
    from . import iai_bpyNodes
    iai_bpyNodes.register()

    registerTypes()
    action_register()
    event_register()


def initialise():
    """Make the classes and functions needed from other files available"""
    sce = bpy.context.scene

    global Simulation
    from .iai_simulate import Simulation

    global update_iai_brains
    from .iai_blenderData import update_iai_brains

    global iai_brains
    iai_brains = bpy.context.scene.iai_brains


def unregister():
    """Called by Blender to remove the add-on. Analogous to the destructor of
    an object but for the add-on instead"""
    bpy.utils.unregister_module(__name__)
    # ...and this one unregisters the SCENE_PT_inaite
    action_unregister()
    event_unregister()
    from .iai_blenderData import unregisterAllTypes
    unregisterAllTypes()

    # iai_bpyNodes.unregister()

if __name__ == "__main__":
    register()
