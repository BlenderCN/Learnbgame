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

bl_info = {
    "name": "Modifier tools",
    "description": "Assorted modifiers manipulation tools",
    "author": "Sergey Sharybin",
    "version": (0, 1),
    "blender": (2, 62, 3),
    "location": "Select an Object: Tool Shelf",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
from bpy.types import Operator, Panel


class OBJECT_OT_copy_modifier_settings(Operator):
    """Copy settings of modifiers from active object to """
    """all other selected objects"""

    bl_idname = "object.copy_modifier_settings"
    bl_label = "Copy Modifier Settings"
    bl_space_type = 'VIEW_3D'

    def execute(self, context):
        # list of properties to be skipped
        skip_props = ("bl_rna", "name", "rna_type", "type")

        obact = context.active_object

        for ob in context.selected_objects:
            if ob == obact:
                continue

            # itterate through all modifiers of active object
            for mod in obact.modifiers:
                if mod.name not in ob.modifiers:
                    # no need to copy modifier to self
                    continue

                mod2 = ob.modifiers[mod.name]

                # copy all propeties from active object to selected
                for prop in dir(mod):
                    if prop.startswith("_") or prop in skip_props:
                        # no need to copy property
                        continue

                    attr = getattr(mod, prop)
                    setattr(mod2, prop, attr)

                # copy animation data for this modifier
                if obact.animation_data and obact.animation_data.action:
                    action = obact.animation_data.action
                    data_path = "modifiers[\"" + mod.name + "\"]"

                    for fcu in action.fcurves:
                        if fcu.data_path.startswith(data_path):
                            # create new animation data if needed
                            if not ob.animation_data:
                                ob.animation_data_create()

                            # if there's no action assigned to selected object
                            # create new one
                            if not ob.animation_data.action:
                                action_name = ob.name + "Action"
                                bpy.data.actions.new(name=action_name)
                                action2 = bpy.data.actions[action_name]
                                ob.animation_data.action = action2
                            else:
                                action2 = ob.animation_data.action

                            # delete existing curve if present
                            for fcu2 in action2.fcurves:
                                if fcu2.data_path == fcu.data_path:
                                    action2.fcurves.remove(fcu2)
                                    break

                            # create new fcurve
                            fcu2 = action2.fcurves.new(data_path=fcu.data_path,
                                index=fcu.array_index)
                            fcu2.color = fcu.color

                            # create keyframes
                            fcu2.keyframe_points.add(len(fcu.keyframe_points))

                            # copy keyframe settings
                            for x in range(len(fcu.keyframe_points)):
                                point = fcu.keyframe_points[x]
                                point2 = fcu2.keyframe_points[x]

                                point2.co = point.co
                                point2.handle_left = point.handle_left
                                point2.handle_left_type = point.handle_left_type
                                point2.handle_right = point.handle_right
                                point2.handle_right_type = point.handle_right_type

        return {'FINISHED'}


class VIEW3D_PT_modifiers(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Modifiers"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.copy_modifier_settings")


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
