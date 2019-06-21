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
'''
Contains GUI elements for working with Neverwinter Nights models in Blender

@author: Erik Ylipää
'''
import bpy

from . import node_props
from . import blend_props


class OBJECT_PT_nwn_colors(bpy.types.Panel):
    bl_idname = "SCENE_PT_nwn_basic_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "NWN Walkmesh Colors"
    bl_context = "vertexpaint"

    def draw(self, context):
        layout = self.layout
        for color in context.scene.nwn_props.walkmesh_colors:
            row = layout.row()
            col = row.prop(color, "color")
            col.active = False
            row.label(text=color.type)


class SCENE_PT_nwn_basic_settings(bpy.types.Panel):
    bl_idname = "SCENE_PT_nwn_basic_settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Basic Model Settings"
    bl_context = "scene"

    def draw(self, context):
        box = self.layout.box()

        box.label(text="Basic model settings")
        box.prop(context.scene.nwn_props, "classification")
        box.prop(context.scene.nwn_props, "supermodel")
        box.prop(context.scene.nwn_props, "animationscale")
        box.prop_search(context.scene.nwn_props, "root_object_name", bpy.data, "objects")


class OBJECT_PT_nwn_animations(bpy.types.Panel):
    bl_idname = "OBJECT_PT_nwn_animations"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Animation tools"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Animations")

        nwn_props = context.scene.nwn_props

        box.operator("scene.add_nwn_anim_set")

        row = box.row()
        col = row.column()
        col.template_list(nwn_props, "animations",
                          nwn_props, "animation_index",
                          rows=3)

        col = row.column(align=True)
        col.operator("scene.add_nwn_anim", icon='ZOOMIN', text="")
        col.operator("scene.remove_nwn_anim", icon='ZOOMOUT', text="")

        if (nwn_props.animations and nwn_props.animation_index >= 0
                and nwn_props.animation_index < len(nwn_props.animations)):
            index = nwn_props.animation_index
            animation = nwn_props.animations[index]

            box.row().operator("scene.nwn_anim_focus")
            anim_row = box.row()
            anim_row.prop(animation, "name")
            anim_row = box.row()
            anim_row.prop_search(animation, "animroot", bpy.data, "objects")

            anim_row = box.row()
            start_marker = animation.get_start_marker()
            end_marker = animation.get_end_marker()
            if start_marker:
                anim_row.prop(start_marker, "frame", text="Start frame")
            else:
                anim_row.operator("scene.nwn_recreate_start_marker").animation = animation.name
            anim_row = box.row()
            if end_marker:
                anim_row.prop(end_marker, "frame", text="End frame")
            else:
                op = anim_row.operator("scene.nwn_recreate_end_marker")
                op.animation = animation.name
            event_box = box.box()
            row = event_box.row()
            row.label(text="Events:")

            row = event_box.row()
            col = row.column()

            col.template_list(animation, "events",
                              animation, "event_index",
                              rows=3, type='DEFAULT')

            col = row.column(align=True)
            col.operator("scene.add_nwn_anim_event", icon='ZOOMIN', text="")
            col.operator("scene.remove_nwn_anim_event", icon='ZOOMOUT', text="")

            if (animation.events and animation.event_index >= 0
                    and animation.event_index < len(animation.events)):
                event = animation.events[animation.event_index]

                row = event_box.row()
                row.prop(event, "type")
                row = event_box.row()
                row.prop(event, "time")


class OBJECT_PT_nwn_node_tools(bpy.types.Panel):
    bl_idname = "OBJECT_PT_nwn_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "NWN Node tools"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if context.object is not None:
            if context.object.type.upper() in ['LAMP', 'MESH', 'EMPTY']:
                return True

        return False

    def draw(self, context):
        layout = self.layout
        obj = context.object
        props = blend_props.get_nwn_props(obj)

        row = layout.row()
        row.prop(props, "is_nwn_object", text="Aurora Object")

        if props.is_nwn_object:
            ### node settings ###
            box = layout.box()

            box.label(text="Node settings")
            node_type = props.nwn_node_type
            box.prop(props, "nwn_node_type")

            if node_type == "danglymesh":
                box.label(text="Dangly Vertex Group:")
                box.prop_search(props, "danglymesh_vertexgroup", obj,
                                "vertex_groups", text="")
            elif node_type == "aabb":
                box.operator("object.nwn_add_walkmesh_materials")
            #box.operator("object.nwn_remove_walkmesh_materials")
            #Compare all possible settings for the specific node_type with the ones
            #loaded into blender
            gui_group_root = node_props.GeometryNodeProperties.get_node_gui_groups(node_type)

            def layout_groups(name, props_, subgroups, parent_box):
                box = parent_box.box()
                box.label(name)
                for prop in props_:
                    if prop.show_in_gui and not prop.blender_ignore:
                        box.prop(props.node_properties, prop.name,
                                 text=prop.gui_name)
                for name, dict in subgroups.items():
                    layout_groups(name, dict["props"], dict["subgroups"], box)

            for name, dict in gui_group_root["subgroups"].items():
                layout_groups(name, dict["props"], dict["subgroups"], box)
