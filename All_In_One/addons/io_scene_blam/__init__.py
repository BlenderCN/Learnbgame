#  Copyright (c) 2019 Oliver Hitchcock ojhitchcock@gmail.com
#
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

# Blender Halo Tools - W.I.P.

bl_info = {
    "name": "Blender Halo Tools",
    "description": "Exporter for Halo CE (JMS) and Halo 2 (ASS) files.",
    "author": "Oliver \"c0rp3n\" Hitchcock",
    "version": (0, 1, 1),
    "blender": (2, 80, 0),
    "category": "Learnbgame",
    "location": "File > Import/Export, Scene properties",
    "warning": "unstable",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/c0rp3n/blender-halo-tools/wiki",
    "tracker_url": "https://github.com/c0rp3n/blender-halo-tools/issues"
}

import bpy
from bpy import ops
from bpy.props import (
    BoolProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
    PointerProperty,
    EnumProperty,
    )

from bpy.types import (
    Panel,
    PropertyGroup
    )

from io_scene_blam import export_jms_model

# ------------------------------------------------------------
# Menu's and panels:
class Blam_SceneProps(Panel):
    bl_label = "Blam Properties"
    bl_idname = "blam_scene_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        blam = scene.blam

        row = layout.row()
        row.prop(blam, "root_collection")

        row = layout.row()
        row.prop(blam, "instance_collection")

class Blam_ObjectProps(Panel):
    bl_label = "Blam Properties"
    bl_idname = "blam_object_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    show_shader_flags: BoolProperty(
        name="Shader Flags",
        default=True,
        description="Show shader flags."
        )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        box = layout.box()
        box.label(text = "Shader Flags")

        flow = box.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)

        obj = context.object
        blam = obj.blam

        col = flow.column()
        col.prop(blam, "double_sided")

        col = flow.column()
        col.prop(blam, "allow_transparency")

        col = flow.column()
        col.prop(blam, "render_only")

        col = flow.column()
        col.prop(blam, "large_collideable")

        col = flow.column()
        col.prop(blam, "fog_plane")

        col = flow.column()
        col.prop(blam, "ladder")

        col = flow.column()
        col.prop(blam, "breakable")

        col = flow.column()
        col.prop(blam, "ai_defeaning")

        col = flow.column()
        col.prop(blam, "exact_portal")

        row = box.row()
        row.prop(blam, "custom_flags")

# ------------------------------------------------------------
# Properties groups:
class Blam_ScenePropertiesGroup(PropertyGroup):
    root_collection : StringProperty(
        name = 'Root',
        default = "Frame",
        description = "The root collection for export"
        )
    
    instance_collection : StringProperty(
        name = 'Instances',
        default = "Assets",
        description = "The instancer collection for export"
        )

class Blam_ObjectPropertiesGroup(PropertyGroup):
    double_sided : BoolProperty(
        name = "Double sided",
        default = False,
        description = "Toggles whether the current object is double sided"
        )

    allow_transparency : BoolProperty(
        name = "Allow transparency",
        default = False,
        description = "Toggles whether the current object is allowed to be transparent"
        )

    render_only : BoolProperty(
        name="Render only",
        default = False,
        description = "Toggles whether the current object is render only"
        )

    large_collideable : BoolProperty(
        name = "Large collideable",
        default = False,
        description = "Toggles whether the current object is a large collideable"
        )

    fog_plane : BoolProperty(
        name = "Fog plane",
        default = False,
        description="Toggles whether the current object is a fog plane"
        )

    ladder : BoolProperty(
        name = "Ladder",
        default = False,
        description = "Toggles whether the current object is a ladder"
        )

    breakable : BoolProperty(
        name = "Breakable",
        default = False,
        description = "Toggles whether the current object is a ladder"
        )

    ai_defeaning : BoolProperty(
        name = "AI deafening",
        default = False,
        description = "Toggles whether the current object shall deafen ai"
        )
    
    collision_only : BoolProperty(
        name = "Collision only",
        default = False,
        description = "Toggles whether the current object shall only be collision"
        )

    exact_portal : BoolProperty(
        name = "Exact Portal",
        default = False,
        description = "Toggles whether the current object is an exact portal"
        )

    custom_flags : StringProperty(
        name = "Custom flag string",
        default = "",
        description = "Allows for a custom flag string, this will overite the boolean flags if not empty"
        )

# ------------------------------------------------------------
# Register:

classes = (
    export_jms_model.Blam_ExportJmsModel,
    Blam_ScenePropertiesGroup,
    Blam_ObjectPropertiesGroup,
    Blam_SceneProps,
    Blam_ObjectProps
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(export_jms_model.menu_func_export)

    bpy.types.Scene.blam = PointerProperty(type=Blam_ScenePropertiesGroup, name="Blam Properties", description="Blam Object properties")
    bpy.types.Object.blam = PointerProperty(type=Blam_ObjectPropertiesGroup, name="Blam Properties", description="Blam Object properties")


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_export.remove(export_jms_model.menu_func_export)

    del bpy.types.Scene.blam
    del bpy.types.Object.blam

if __name__ == "__main__":
    register()