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
Contains operators used for creating Neverwinter Nights models in Blender.

This module contains all operators used from the Borealis GUI to interact
with Neverwinter Nights specific data in Blender.

@author: Erik Ylipää
'''
import bpy
import mathutils
from mathutils import Color

from . import basic_props
from . import blend_props
from . import animation_names

ANIMATION_FRAME_GAP = 10


class SCENE_OT_remove_nwn_animation(bpy.types.Operator):
    """ Operator which removes an nwn animation from the scene object """

    bl_idname = "scene.remove_nwn_anim"
    bl_label = "Remove NWN animation"

    animation_name = bpy.props.StringProperty("Name of animation to remove")

    @classmethod
    def poll(cls, context):
        if context.scene.nwn_props.animations:
            return True
        else:
            return False

    def execute(self, context):
        anim_props = context.scene.nwn_props
        index = anim_props.animation_index
        scene = context.scene

        animation = anim_props.animations[index]
        m = animation.start_marker
        scene.timeline_markers.remove(m)
        m = animation.end_marker
        scene.timeline_markers.remove(m)
        anim_props.animations.remove(index)
        context.area.tag_redraw()  # force the gui to redraw
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class SCENE_OT_add_nwn_animation(bpy.types.Operator):
    """ Adds a new Neverwinter Nights animation to the scene object """

    bl_idname = "scene.add_nwn_anim"
    bl_label = "Add a new NWN animation"

    name = bpy.props.StringProperty(name="Animation name", default="Unnamed")
    length = bpy.props.IntProperty(name="Animation length (frames)", default=50, min=0)
    names = bpy.props.CollectionProperty(type=blend_props.AnimationName)

    def execute(self, context):
        scene = context.scene
        #find the last marker to get a good place to insert the new animation
        last_frame = 0
        for marker in scene.timeline_markers:
            if marker.frame > last_frame:
                last_frame = marker.frame

        start_frame = last_frame + ANIMATION_FRAME_GAP
        end_frame = start_frame + self.length

        anim_ob = scene.nwn_props.animations.add()
        anim_ob.name = self.name
        anim_ob.start_frame = start_frame
        anim_ob.end_frame = end_frame

        context.area.tag_redraw()  # force the gui to redraw

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        classification = context.scene.nwn_props.classification
        names = animation_names.get_names()[classification]
        if classification.lower() == "character":
            new_names = []
            for subclass, sub_names in names.items():
                new_names.extend(sub_names)
            names = new_names

        for name in names:
            new_name = self.names.add()
            new_name.name = name
        print(self.names[:])
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        #Prop search is buggy, we use a simple input field for now
        #col.prop_search(self, "name", self, "names")
        col.prop(self, "name")
        col.prop(self, "length")


class SCENE_OT_remove_nwn_anim_event(bpy.types.Operator):
    """ Removes the currently selected event in the current animation """

    bl_idname = "scene.remove_nwn_anim_event"
    bl_label = "Remove an event from a NWN animation"

    @classmethod
    def poll(cls, context):
        anim_props = context.scene.nwn_props

        if anim_props.animations:
            index = anim_props.animation_index
            animation = anim_props.animations[index]

            if animation.events:
                return True

        return False

    def execute(self, context):
        anim_props = context.scene.nwn_props
        index = anim_props.animation_index

        animation = anim_props.animations[index]

        event_index = animation.event_index
        animation.events.remove(event_index)
        context.area.tag_redraw()  # force the gui to redraw
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class SCENE_OT_add_nwn_anim_event(bpy.types.Operator):
    """ Adds a new event to the selected animation """

    bl_idname = "scene.add_nwn_anim_event"
    bl_label = "Add a new event to a NWN animation"

    @classmethod
    def poll(cls, context):
        anim_props = context.scene.nwn_props

        if anim_props.animations:
            return True

        return False

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self.event, "type")
        row = layout.row()
        row.prop(self.event, "time")

    def execute(self, context):
        self.event.update_name(None)

        context.area.tag_redraw()  # force the gui to redraw

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager

        anim_props = context.scene.nwn_props
        index = anim_props.animation_index
        animation = anim_props.animations[index]
        self.event = animation.events.add()

        return wm.invoke_props_dialog(self)


class SCENE_OT_nwn_anim_focus(bpy.types.Operator):
    """ Adjust scene start and end frame to the selected animation """

    bl_idname = "scene.nwn_anim_focus"
    bl_label = "Focus on animation"
    bl_description = "Adjust scene start and end frame to the selected animation"

    @classmethod
    def poll(cls, context):
        if context.scene.nwn_props.animations:
            return True
        else:
            return False

    def execute(self, context):
        scene = context.scene

        anim_props = context.scene.nwn_props
        index = anim_props.animation_index

        animation = anim_props.animations[index]
        start_frame = animation.start_frame
        scene.frame_start = start_frame
        scene.frame_end = animation.end_frame
        scene.frame_current = start_frame
        scene.frame_start = start_frame  # for some reason there's a bug if frame_start is set only once

        return {'FINISHED'}


class SCENE_OT_remove_all_nwn_anims(bpy.types.Operator):
    """
        Removes all Neverwinter Nights Animations
    """
    bl_idname = "scene.remove_all_nwn_anims"
    bl_label = "Remove all animations"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)


class SCENE_OT_add_nwn_anim_set(bpy.types.Operator):
    """ Adds a complete set of animations according to the selected category """
    bl_idname = "scene.add_nwn_anim_set"
    bl_label = "Add all animations"

    def get_categories(self, context):
        classification = context.scene.nwn_props.classification.lower()
        names = animation_names.get_names()[classification]
        if isinstance(names, dict):
            items = [(item, item, item) for item in names.keys()]
        else:
            items = [(classification, classification, classification)]
        return items

    categories = bpy.props.EnumProperty(name="Subcategory", items=get_categories)
    animation_root = bpy.props.StringProperty(name="Animation Root")
    length = 50

    def draw(self, context):
        layout = self.layout
        classification = context.scene.nwn_props.classification
        col = layout.column()
        col.label(text="Adding animations for model class %s" % classification.capitalize())
        if classification.lower() == "character":
            col.prop(self, "categories")
        col.prop_search(self, "animation_root", context.scene, "objects")

    def execute(self, context):
        scene = context.scene
        #find the last marker to get a good place to insert the new animation
        last_frame = 0
        for marker in scene.timeline_markers:
            if marker.frame > last_frame:
                last_frame = marker.frame
        start_frame = last_frame + ANIMATION_FRAME_GAP
        last_frame = start_frame + self.length

        classification = context.scene.nwn_props.classification.lower()
        names = animation_names.get_names()[classification]
        if classification.lower() == "character":
            new_names = []
            for subclass, sub_names in names.items():
                new_names.extend(sub_names)
            names = new_names

        for name in names:
            if name in context.scene.nwn_props.animations:
                continue
            anim_ob = scene.nwn_props.animations.add()
            anim_ob.name = name
            anim_ob.start_frame = start_frame
            anim_ob.end_frame = last_frame
            anim_ob.animroot = self.animation_root
            start_frame = last_frame + ANIMATION_FRAME_GAP
            last_frame = start_frame + self.length

        context.area.tag_redraw()  # force the gui to redraw

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class OBJECT_OT_create_walkmesh_materials(bpy.types.Operator):
    bl_idname = "object.nwn_add_walkmesh_materials"
    bl_label = "Add Walkmesh materials"
    bl_description = "Adds walkmesh materials for the selected mesh object"

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            return obj.type == 'MESH'
        return False

    def execute(self, context):
        blend_props.create_walkmesh_materials(context.object)
        return {'FINISHED'}


class OBJECT_OT_nwn_remove_walkmesh_materials(bpy.types.Operator):
    bl_idname = "object.nwn_remove_walkmesh_materials"
    bl_label = "Remove Walkmesh materials"
    bl_description = "Removes walkmesh materials for the selected mesh object"

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj:
            return obj.type == 'MESH'
        return False

    def execute(self, context):
        blend_props.remove_walkmesh_materials(context.object)
        return {'FINISHED'}


class SCENE_OT_nwn_recreate_start_marker(bpy.types.Operator):
    bl_idname = "scene.nwn_recreate_start_marker"
    bl_label = "Recreate start marker"
    bl_description = "Recreates the start marker of the selected animation"

    animation = bpy.props.StringProperty(name="Animation object name")

    def execute(self, context):
        animation = context.scene.nwn_props.animations[self.animation]
        animation.create_start_marker()
        return {'FINISHED'}


class SCENE_OT_nwn_recreate_end_marker(bpy.types.Operator):
    bl_idname = "scene.nwn_recreate_end_marker"
    bl_label = "Recreate end marker"
    bl_description = "Recreates the end marker of the selected animation"

    animation = bpy.props.StringProperty(name="Animation object name")

    def execute(self, context):
        animation = context.scene.nwn_props.animations[self.animation]
        animation.create_end_marker()
        return {'FINISHED'}
