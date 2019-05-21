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

import bpy

#
# Custom Property Groups
#


class PreflightMeshGroup(bpy.types.PropertyGroup):
    """Property group of mesh names."""

    obj_pointer = bpy.props.PointerProperty(
        name="Object Pointer",
        type=bpy.types.Object,
        description="Object to Export")

    obj_name = bpy.props.StringProperty(
        name="Object Name",
        description="Name of the object to export. Note: If the object name changes, the reference will be lost.",
        default="")


class PreflightExportGroup(bpy.types.PropertyGroup):
    """Property group of export options."""

    is_collapsed = bpy.props.BoolProperty(
        name="Collapse Group",
        description="Collapse the display of this export group.",
        default=False)
    name = bpy.props.StringProperty(
        name="Export Group Name",
        description="File name for this export group. Will be converted to camel case. Duplicate names will cause an error.",
        default="")
    include_animations = bpy.props.BoolProperty(
        name="Include Animations",
        description="Include animations along with the armatures in this export group.",
        default=False)
    apply_modifiers = bpy.props.BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers while performing this export.",
        default=True)
    obj_names = bpy.props.CollectionProperty(type=PreflightMeshGroup)
    obj_idx = bpy.props.IntProperty(name="Object Index", default=0)


class PreflightExportOptionsGroup(bpy.types.PropertyGroup):
    allowed_keys = [
        "axis_up",
        "axis_forward",
        "bake_space_transform",
        "version",
        "use_selection",
        "object_types",
        "use_mesh_modifiers",
        "mesh_smooth_type",
        "use_mesh_edges",
        "use_tspace",
        "use_custom_props",
        "add_leaf_bones",
        "primary_bone_axis",
        "secondary_bone_axis",
        "use_armature_deform_only",
        "bake_anim",
        "bake_anim_use_all_bones",
        "bake_anim_use_nla_strips",
        "bake_anim_use_all_actions",
        "bake_anim_step",
        "bake_anim_simplify_factor",
        "use_anim",
        "use_anim_action_all",
        "use_default_take",
        "use_anim_optimize",
        "anim_optimize_precision",
        "path_mode",
        "embed_textures",
        "batch_mode",
        "use_batch_own_dir",
    ]

    axis_enum = [
        ('X', 'X Axis', ''),
        ('Y', 'Y Axis', ''),
        ('Z', 'Z Axis', ''),
        ('-X', '-X Axis', ''),
        ('-Y', '-Y Axis', ''),
        ('-Z', '-Z Axis', ''),
    ]

    object_types_enum = [
        ('MESH', "Meshes", "Export Meshes"),
        ('ARMATURE', "Armatures", "Export Armatures"),
        ('EMPTY', "Empty", ""),
        ('OTHER', "Other", "Other geometry types, like curve, metaball, etc. (converted to meshes)")
    ]

    def as_dict(self):
        return {key: getattr(self, key) for key in dict(self).keys()}

    def reset(self, options):
        for key, value in options:
            if hasattr(self, key):
                setattr(self, key, value)

    def defaults_for_unity(self, **overrides):
        defaults = dict(
            version='BIN7400',
            axis_up='Y',
            axis_forward='-Z',
            bake_space_transform=True,
            use_selection=True,
            object_types={'MESH', 'ARMATURE', 'EMPTY', 'OTHER'},
            use_mesh_modifiers=True,
            mesh_smooth_type='OFF',
            use_mesh_edges=False,
            use_tspace=False,
            use_custom_props=False,
            add_leaf_bones=True,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            use_armature_deform_only=False,
            bake_anim=True,
            bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=True,
            bake_anim_use_all_actions=True,
            bake_anim_step=1.0,
            bake_anim_simplify_factor=1.0,
            use_anim=True,
            use_anim_action_all=True,
            use_default_take=True,
            use_anim_optimize=True,
            anim_optimize_precision=6.0,
            path_mode='AUTO',
            embed_textures=False,
            batch_mode='OFF',
            use_batch_own_dir=True,
        )

        return {**defaults, **overrides}

    def get_options_dict(self, **overrides):
        """return all options, filtered to valid selections"""
        opts = {**self.defaults_for_unity(), **self.as_dict(), **overrides}
        return dict((k, opts[k]) for k in self.allowed_keys if k in opts)

    # Axis Properties
    object_types = bpy.props.EnumProperty(name="Object Types", items=object_types_enum, default={
                                          'ARMATURE', 'MESH', 'EMPTY', 'OTHER'}, options={'ENUM_FLAG'})
    axis_up = bpy.props.EnumProperty(name="Up", items=axis_enum, default="Y")
    axis_forward = bpy.props.EnumProperty(
        name="Forward", items=axis_enum, default="-Z")
    use_anim = bpy.props.BoolProperty(name="Use Animations", default=True)

    bake_anim_step = bpy.props.FloatProperty(
        name="Sampling Rate",
        description="How often to evaluate animated values (in frames)",
        min=0.01, max=100.0,
        soft_min=0.1, soft_max=10.0,
        default=1.0)

    bake_anim_simplify_factor = bpy.props.FloatProperty(
        name="Simplify",
        description="How much to simplify baked values (0.0 to disable, the higher the more simplified)",
        min=0.0, max=100.0,
        soft_min=0.0, soft_max=10.0,
        default=1.0)

    separate_animations = bpy.props.BoolProperty(
        name="Export Animations to Separate File",
        description="Include all animations in a separate animations file.",
        default=True)

    export_location = bpy.props.StringProperty(
        name="Export To",
        description="Choose an export location. Relative location prefixed with '//'.",
        default="//preflight",
        maxlen=1024,
        subtype='DIR_PATH')


class PreflightOptionsGroup(bpy.types.PropertyGroup):
    """Parent property group for preflight."""

    export_options = bpy.props.PointerProperty(
        type=PreflightExportOptionsGroup)
    fbx_export_groups = bpy.props.CollectionProperty(type=PreflightExportGroup)
